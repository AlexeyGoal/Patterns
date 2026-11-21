from Src.Core.entity import entity
from Src.Core.exception import arguments_exception
from Src.Core.validator import operation_exception
from Src.Dtos.filter_dto import filter_dto
from Src.Logics.deserialize_service import deserialize_service
from Src.Logics.entity_mapper import entity_mapper
from Src.Logics.entity_references import entity_references
from Src.Logics.entity_registry import entity_metadata_registry
from Src.Logics.entity_store import entity_store
from Src.Logics.filter_prototype import filter_prototype
from Src.Logics.serialize_factory import serialize_factory
from Src.Logics.storage_manager import storage_manager


"""
Сервис CRUD-операций над доменными сущностями.
"""
class entity_service:

    def __init__(self, manager: storage_manager = None):

        self.__store = entity_store(manager)
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
        self.__prototype = filter_prototype()


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
        return [
            self.__mapper.to_dto(item)
            for item in self.__store.values(normalized_type)
        ]


    # Отфильтровать сущности указанного типа по DTO фильтрации
    def filter_entities(
        self,
        entity_type: str,
        query: filter_dto,
    ) -> list[dict]:

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

        items = self.__store.values(normalized_type)
        prototype = self.__prototype.clone(query)

        return [
            self.__mapper.to_dto(item)
            for item in prototype.filter(items)
        ]


    # Одна сущность по коду в JSON-совместимом виде
    def get_entity(self, entity_type: str, entity_code: str) -> dict | None:
        item = self._find(entity_type, entity_code)
        return self.__mapper.to_dto(item) if item is not None else None


    # Создать доменную сущность
    def create_entity(self, entity_type: str, payload: dict) -> dict:
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

        return self.__mapper.to_dto(model)


    # Изменить доменную сущность
    def update_entity(self, entity_type: str, entity_code: str, payload: dict) -> dict:
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

        return self.__mapper.to_dto(updated)


    # Удалить доменную сущность
    def delete_entity(self, entity_type: str, entity_code: str) -> dict:
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

        return self.__mapper.to_dto(existing)


    # Преобразовать модель в JSON-совместимый словарь
    def to_dict(self, item: entity) -> dict:
        return self.__mapper.to_dto(item)


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
