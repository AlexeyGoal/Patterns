from Src.Core.entity import entity
from Src.Core.exception import arguments_exception
from Src.Core.log_type import log_category, log_operation, log_status
from Src.Core.validator import operation_exception
from Src.Dtos.filter_dto import filter_dto
from Src.Dtos.log_event_dto import log_event_dto
from Src.Logics.deserialize_service import deserialize_service
from Src.Logics.entity_mapper import entity_mapper
from Src.Logics.entity_references import entity_references
from Src.Logics.entity_registry import entity_metadata_registry
from Src.Logics.entity_store import entity_store
from Src.Logics.filter_prototype import filter_prototype
from Src.Logics.logging_service import logging_service
from Src.Logics.osv_service import osv_service
from Src.Logics.serialize_factory import serialize_factory
from Src.Logics.storage_manager import storage_manager


"""
Сервис CRUD-операций над доменными сущностями.
"""
class entity_service:

    def __init__(
        self,
        manager: storage_manager = None,
        logger: logging_service = None,
    ):

        self.__manager = manager if manager is not None else storage_manager()
        self.__logger = logger if logger is not None else logging_service()
        self.__store = entity_store(self.__manager)
        self.__serializer = serialize_factory()
        self.__deserializer = deserialize_service()
        self.__registry = entity_metadata_registry(self.__deserializer.model_types)
        self.__mapper = entity_mapper(
            self.__registry,
            self.__serializer,
            self.__deserializer,
            self.__store.find,
        )
        self.__references = entity_references(self.__registry, self.__store)
        self.__prototype = filter_prototype(source=self.__store.values)
        self.__osv = osv_service(self.__manager, self.__prototype)


    # Поддерживаемые сервисом типы сущностей
    @property
    def supported_types(self) -> list[str]:
        return self.__registry.types


    # Поддерживается ли тип сущности
    def supports(self, entity_type: str) -> bool:
        return self.__registry.supports(entity_type)


    # Список сущностей указанного типа в JSON-совместимом виде
    def list_entities(self, entity_type: str) -> list[dict]:
        normalized_type = self.__require_type(entity_type)
        result = [
            self.__mapper.to_dto(item)
            for item in self.__store.values(normalized_type)
        ]

        self.__log(
            log_operation.READ,
            normalized_type,
            message=f"Получен список сущностей типа '{normalized_type}'",
            details={"count": len(result)},
        )

        return result


    # Отфильтровать сущности указанного типа по DTO фильтрации
    def filter_entities(
        self,
        entity_type: str,
        query: filter_dto,
    ) -> list[dict]:

        try:
            normalized_type = self.__require_type(entity_type)

            if not isinstance(query, filter_dto):
                raise arguments_exception("query", "Ожидался DTO фильтрации")

            if query.entity_type != normalized_type:
                raise arguments_exception(
                    "entity_type",
                    f"DTO фильтрации относится к типу '{query.entity_type}', "
                    f"а запрошен тип '{normalized_type}'",
                )

            metadata = self.__registry.get(normalized_type)
            self.__prototype.resolve_field(metadata.model, query.field_name)

            prototype = self.__prototype.clone(query)
            result = [
                self.__mapper.to_dto(item)
                for item in prototype.items
            ]

        except Exception as ex:
            self.__log(
                log_operation.READ,
                self.__normalize_for_log(entity_type),
                status=log_status.FAILURE,
                message=f"Ошибка фильтрации сущностей: {ex}",
                details={"field_name": getattr(query, "field_name", "")},
            )
            raise

        self.__log(
            log_operation.READ,
            normalized_type,
            message=f"Отфильтрованы сущности типа '{normalized_type}'",
            details={
                "count": len(result),
                "field_name": query.field_name,
                "value": query.value,
                "filter_type": query.filter_type.value,
            },
        )

        return result


    # Сформировать оборотно-сальдовую ведомость с учетом фильтрации
    def build_osv(
        self,
        query: filter_dto,
        start_date: object = None,
    ) -> list[dict]:

        try:
            if not isinstance(query, filter_dto):
                raise arguments_exception("query", "Ожидался DTO фильтрации")

            normalized_type = self.__require_type(query.entity_type)

            if normalized_type != osv_service.ENTITY_TYPE:
                raise arguments_exception(
                    "entity_type",
                    f"ОСВ формируется только по типу '{osv_service.ENTITY_TYPE}', "
                    f"а передан тип '{normalized_type}'",
                )

            result = self.__osv.build_serialized(query, start_date)

        except Exception as ex:
            self.__log(
                log_operation.REPORT,
                osv_service.ENTITY_TYPE,
                category=log_category.WAREHOUSE,
                status=log_status.FAILURE,
                message=f"Ошибка формирования ОСВ: {ex}",
                details={"start_date": start_date},
            )
            raise

        self.__log(
            log_operation.REPORT,
            normalized_type,
            category=log_category.WAREHOUSE,
            message="Сформирована оборотно-сальдовая ведомость",
            details={
                "count": len(result),
                "start_date": start_date,
                "field_name": query.field_name,
                "value": query.value,
            },
        )

        return result


    # Одна сущность по коду в JSON-совместимом виде
    def get_entity(self, entity_type: str, entity_code: str) -> dict | None:
        item = self._find(entity_type, entity_code)
        normalized_type = self.__normalize_for_log(entity_type)
        result = self.__mapper.to_dto(item) if item is not None else None

        self.__log(
            log_operation.READ,
            normalized_type,
            entity_code=entity_code,
            status=log_status.SUCCESS if result is not None else log_status.FAILURE,
            message=(
                f"Получена сущность типа '{normalized_type}'"
                if result is not None
                else f"Сущность типа '{normalized_type}' с кодом '{entity_code}' не найдена"
            ),
        )

        return result


    # Создать доменную сущность
    def create_entity(self, entity_type: str, payload: dict) -> dict:
        normalized_type = self.__normalize_for_log(entity_type)

        try:
            normalized_type = self.__require_type(entity_type)

            if not isinstance(payload, dict):
                raise arguments_exception("payload", "Тело запроса должно быть JSON-объектом")

            prepared = self.__mapper.prepare(normalized_type, payload)
            model = self.__mapper.restore(normalized_type, prepared)

            if self._find(normalized_type, model.id) is not None:
                raise operation_exception(
                    f"Сущность типа '{normalized_type}' с кодом '{model.id}' уже существует"
                )

            if not self.__store.add(normalized_type, model):
                raise operation_exception(
                    f"Не удалось сохранить сущность типа '{normalized_type}'"
                )

            result = self.__mapper.to_dto(model)

        except Exception as ex:
            self.__log(
                log_operation.CREATE,
                normalized_type,
                status=log_status.FAILURE,
                message=f"Ошибка создания сущности: {ex}",
                details={"payload": payload},
            )
            raise

        self.__log(
            log_operation.CREATE,
            normalized_type,
            entity_code=model.id,
            message=f"Создана сущность типа '{normalized_type}'",
            details={"name": model.name},
        )

        return result


    # Изменить доменную сущность
    def update_entity(self, entity_type: str, entity_code: str, payload: dict) -> dict:
        normalized_type = self.__normalize_for_log(entity_type)

        try:
            normalized_type = self.__require_type(entity_type)
            existing = self._find(normalized_type, entity_code)

            if existing is None:
                raise operation_exception(
                    f"Сущность типа '{normalized_type}' с кодом '{entity_code}' не найдена"
                )

            if not isinstance(payload, dict):
                raise arguments_exception("payload", "Тело запроса должно быть JSON-объектом")

            # Берём текущее состояние и накладываем изменения - так частичное
            # изменение не требует передавать все поля сущности.
            data = self.__mapper.merge(existing, payload)

            original_id = str(existing.id)
            requested_id = str(data.get("id", original_id))

            if requested_id != original_id:
                dependents = self._find_dependents(normalized_type, existing)
                if dependents:
                    raise operation_exception(
                        "Запрещено изменять код сущности, так как она связана с другими "
                        f"доменными сущностями: {self.__references.format_dependents(dependents)}"
                    )

            prepared = self.__mapper.prepare(normalized_type, data)
            updated = self.__mapper.restore(normalized_type, prepared)

            if requested_id != original_id and self._find(normalized_type, requested_id) is not None:
                raise operation_exception(
                    f"Сущность типа '{normalized_type}' с кодом '{requested_id}' уже существует"
                )

            collection = self.__store.collection(normalized_type)
            collection.pop(existing.id, None)

            if not self.__store.add(normalized_type, updated):
                # Возвращаем исходную сущность, если сохранение не удалось
                collection[existing.id] = existing
                raise operation_exception(
                    f"Не удалось изменить сущность типа '{normalized_type}'"
                )

            before = self.__mapper.to_dto(existing)
            result = self.__mapper.to_dto(updated)

        except Exception as ex:
            self.__log(
                log_operation.UPDATE,
                normalized_type,
                entity_code=entity_code,
                status=log_status.FAILURE,
                message=f"Ошибка изменения сущности: {ex}",
                details={"payload": payload},
            )
            raise

        self.__log(
            log_operation.UPDATE,
            normalized_type,
            entity_code=entity_code,
            message=f"Изменена сущность типа '{normalized_type}'",
            details={
                "name": updated.name,
                "changes": self.__diff(before, result),
            },
        )

        return result


    # Удалить доменную сущность
    def delete_entity(self, entity_type: str, entity_code: str) -> dict:
        normalized_type = self.__normalize_for_log(entity_type)

        try:
            normalized_type = self.__require_type(entity_type)
            existing = self._find(normalized_type, entity_code)

            if existing is None:
                raise operation_exception(
                    f"Сущность типа '{normalized_type}' с кодом '{entity_code}' не найдена"
                )

            dependents = self._find_dependents(normalized_type, existing)
            if dependents:
                raise operation_exception(
                    "Запрещено удалять сущность, так как она связана с другими "
                    f"доменными сущностями: {self.__references.format_dependents(dependents)}"
                )

            self.__store.remove(normalized_type, existing)
            result = self.__mapper.to_dto(existing)

        except Exception as ex:
            self.__log(
                log_operation.DELETE,
                normalized_type,
                entity_code=entity_code,
                status=log_status.FAILURE,
                message=f"Ошибка удаления сущности: {ex}",
            )
            raise

        self.__log(
            log_operation.DELETE,
            normalized_type,
            entity_code=entity_code,
            message=f"Удалена сущность типа '{normalized_type}'",
            details={"name": existing.name},
        )

        return result


    # Преобразовать модель в JSON-совместимый словарь
    def to_dict(self, item: entity) -> dict:
        return self.__mapper.to_dto(item)


    # Записать событие CRUD/складской операции в журнал
    def __log(
        self,
        operation: object,
        entity_type: str,
        entity_code: object = "",
        status: object = log_status.SUCCESS,
        message: str = "",
        details: dict = None,
        category: object = None,
    ) -> None:

        try:
            event = log_event_dto(
                category=(
                    category
                    if category is not None
                    else self.__category_for(entity_type)
                ),
                operation=operation,
                status=status,
                entity_type=entity_type,
                entity_code=str(entity_code or ""),
                message=message,
                details=details,
                source="entity_service",
            )
            self.__logger.log(event)
        except Exception:
            # Сбой журналирования не должен прерывать CRUD-операцию.
            pass


    # Категория журнала: операции со складами относятся к складским
    @staticmethod
    def __category_for(entity_type: str) -> log_category:

        if entity_service.__normalize_for_log(entity_type) == "storage":
            return log_category.WAREHOUSE

        return log_category.CRUD


    # Нормализовать тип сущности для журнала
    @staticmethod
    def __normalize_for_log(entity_type: str) -> str:
        return str(entity_type or "").strip().lower()


    # Разница между состоянием сущности до и после изменения
    @staticmethod
    def __diff(before: dict, after: dict) -> dict:

        changes = {}
        before = before if isinstance(before, dict) else {}
        after = after if isinstance(after, dict) else {}

        for field in sorted(set(before) | set(after)):
            old_value = before.get(field)
            new_value = after.get(field)

            if old_value != new_value:
                changes[field] = {
                    "before": old_value,
                    "after": new_value,
                }

        return changes


    # Проверить, что тип поддерживается сервисом
    def __require_type(self, entity_type: str) -> str:

        metadata = self.__registry.get(entity_type)

        if metadata is None:
            raise arguments_exception(
                "entity_type",
                f"Неподдерживаемый тип сущности: '{entity_type}'. "
                f"Допустимые значения: {', '.join(self.supported_types)}",
            )

        return metadata.api_type


    # Найти сущность по типу и коду
    def _find(self, entity_type: str, entity_code: str) -> entity | None:

        metadata = self.__registry.get(entity_type)

        if metadata is None:
            return None

        return self.__store.find(metadata.api_type, entity_code)


    # Найти сущности, которые ссылаются на указанную сущность
    def _find_dependents(
        self,
        entity_type: str,
        item: entity,
    ) -> list[tuple[str, entity]]:

        return self.__references.find_dependents(entity_type, item)


EntityService = entity_service
