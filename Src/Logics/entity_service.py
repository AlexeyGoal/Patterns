from Src.Core.entity import entity
from Src.Core.exception import arguments_exception
from Src.Core.validator import operation_exception
from Src.Logics.deserialize_service import deserialize_service
from Src.Logics.serialize_factory import serialize_factory
from Src.Logics.storage_manager import storage_manager
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.recipe_item_model import recipe_item_model
from Src.Models.recipe_model import recipe_model
from Src.Models.storage_model import storage_model


"""
Сервис CRUD-операций над доменными сущностями.
"""
class entity_service:

    # Тип сущности API -> класс доменной модели
    _MODELS = {
        "recipe": recipe_model,
        "nomenclature": nomenclature_model,
        "range": range_model,
        "group": nomenclature_group_model,
        "storage": storage_model,
    }

    # Встроенные модели, которые не хранятся отдельной коллекцией
    _EMBEDDED_MODELS = {
        "recipe_item": recipe_item_model,
    }

    # Тип сущности API -> имя публичной коллекции storage_manager
    _COLLECTIONS = {
        "recipe": "recipes",
        "nomenclature": "nomenclatures",
        "range": "ranges",
        "group": "groups",
        "storage": "storages",
    }

    # Тип сущности API -> метод добавления storage_manager
    _ADDERS = {
        "recipe": "add_recipe",
        "nomenclature": "add_nomenclature",
        "range": "add_range",
        "group": "add_group",
        "storage": "add_storage",
    }

    # Допустимые псевдонимы полей входного JSON
    _FIELD_ALIASES = {
        "code": "id",
        "unique_code": "id",
        "group_id": "group",
        "range_id": "range",
        "unit": "range",
        "unit_id": "range",
        "base_range_id": "base_range",
        "sub_recipe_ids": "sub_recipes",
        "recipe_ids": "sub_recipes",
        "item_type": "type",
    }

    # Связи модели: поле -> (тип связанной сущности, коллекция, встроенная модель)
    _RELATIONS = {
        "nomenclature": {
            "group": ("group", False, False),
            "range": ("range", False, False),
        },
        "range": {
            "base_range": ("range", False, False),
        },
        "recipe": {
            "items": ("recipe_item", True, True),
            "sub_recipes": ("recipe", True, False),
            "packaging": ("recipe_item", False, True),
        },
        "recipe_item": {
            "range": ("range", False, False),
            "items": ("recipe_item", True, True),
        },
    }


    def __init__(self, manager: storage_manager = None):

        self.__manager = manager if manager is not None else storage_manager()
        self.__serializer = serialize_factory()
        self.__deserializer = deserialize_service()


    # Поддерживаемые сервисом типы сущностей
    @property
    def supported_types(self) -> list[str]:
        return list(self._MODELS.keys())


    # Поддерживается ли тип сущности
    def supports(self, entity_type: str) -> bool:
        return self._normalize(entity_type) in self._MODELS


    # Список сущностей указанного типа в JSON-совместимом виде
    def list_entities(self, entity_type: str) -> list[dict]:
        return [
            self.__to_dto(item)
            for item in self.__collection(entity_type).values()
        ]


    # Одна сущность по коду в JSON-совместимом виде
    def get_entity(self, entity_type: str, entity_code: str) -> dict | None:
        item = self._find(entity_type, entity_code)
        return self.__to_dto(item) if item is not None else None


    # Создать доменную сущность
    def create_entity(self, entity_type: str, payload: dict) -> dict:
        normalized_type = self.__require_type(entity_type)

        if not isinstance(payload, dict):
            raise arguments_exception("payload", "Тело запроса должно быть JSON-объектом")

        payload = self.__apply_aliases(payload)
        prepared = self.__prepare_payload(normalized_type, payload)
        model = self.__restore(normalized_type, prepared)

        if self._find(normalized_type, model.id) is not None:
            raise operation_exception(
                f"Сущность типа '{normalized_type}' с кодом '{model.id}' уже существует"
            )

        if not self._add(normalized_type, model):
            raise operation_exception(
                f"Не удалось сохранить сущность типа '{normalized_type}'"
            )

        return self.__to_dto(model)


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

        payload = self.__apply_aliases(payload)

        # Берём текущее состояние и накладываем изменения - так частичное
        # изменение не требует передавать все поля сущности.
        data = self.__serializer.convert(existing)
        for field, value in payload.items():
            data[field] = value

        original_id = str(existing.id)
        requested_id = str(data.get("id", original_id))

        if requested_id != original_id:
            dependents = self._find_dependents(normalized_type, existing)
            if dependents:
                raise operation_exception(
                    "Запрещено изменять код сущности, так как она связана с другими "
                    f"доменными сущностями: {self.__format_dependents(dependents)}"
                )

        prepared = self.__prepare_payload(normalized_type, data)
        updated = self.__restore(normalized_type, prepared)

        if requested_id != original_id and self._find(normalized_type, requested_id) is not None:
            raise operation_exception(
                f"Сущность типа '{normalized_type}' с кодом '{requested_id}' уже существует"
            )

        collection = self.__collection(normalized_type)
        collection.pop(existing.id, None)

        if not self._add(normalized_type, updated):
            # Возвращаем исходную сущность, если сохранение не удалось
            collection[existing.id] = existing
            raise operation_exception(
                f"Не удалось изменить сущность типа '{normalized_type}'"
            )

        return self.__to_dto(updated)


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
                f"доменными сущностями: {self.__format_dependents(dependents)}"
            )

        self.__collection(normalized_type).pop(existing.id, None)

        return self.__to_dto(existing)


    # Преобразовать модель в JSON-совместимый словарь
    def to_dict(self, item: entity) -> dict:
        return self.__to_dto(item)


    # JSON-представление сущности с дополнительным алиасом кода
    def __to_dto(self, item: entity) -> dict:

        data = self.__serializer.convert(item)

        if isinstance(data, dict):
            data.setdefault("code", data.get("id"))

        return data


    # Проверить, что тип поддерживается сервисом
    def __require_type(self, entity_type: str) -> str:

        normalized_type = self._normalize(entity_type)
        if normalized_type not in self._MODELS:
            raise arguments_exception(
                "entity_type",
                f"Неподдерживаемый тип сущности: '{entity_type}'. "
                f"Допустимые значения: {', '.join(self.supported_types)}",
            )

        return normalized_type


    # Публичная коллекция сущностей в storage_manager
    def __collection(self, entity_type: str) -> dict:

        return getattr(self.__manager, self._COLLECTIONS[entity_type])


    # Найти сущность по типу и коду
    def _find(self, entity_type: str, entity_code: str) -> entity | None:

        normalized_type = self._normalize(entity_type)
        if normalized_type not in self._MODELS:
            return None

        for item in self.__collection(normalized_type).values():
            if str(item.id) == str(entity_code):
                return item

        return None


    # Добавить модель в коллекцию storage_manager
    def _add(self, entity_type: str, item: entity) -> bool:

        return getattr(self.__manager, self._ADDERS[entity_type])(item)


    # Восстановить модель общим механизмом десериализации и связать ссылки с хранилищем
    def __restore(self, entity_type: str, prepared: dict) -> entity:

        restored = self.__deserializer.deserialize(prepared)
        model_type = self._MODELS[entity_type]

        if not isinstance(restored, model_type):
            raise arguments_exception(
                "payload",
                f"Не удалось создать сущность типа '{entity_type}'",
            )

        self.__rebind(entity_type, restored)
        self.__validate(entity_type, restored)
        return restored


    # Дополнительные проверки корректности доменной модели
    def __validate(self, entity_type: str, model: entity) -> None:

        if entity_type != "range":
            return

        visited = {model.id}
        current = model.base_range

        while current is not None:
            if current.id in visited:
                raise arguments_exception(
                    "base_range", "Обнаружена циклическая ссылка базовых единиц измерения"
                )

            visited.add(current.id)
            current = current.base_range


    # Привести псевдонимы полей входного JSON к каноническим именам
    @classmethod
    def __apply_aliases(cls, payload: dict) -> dict:

        prepared = dict(payload)

        for alias, target in cls._FIELD_ALIASES.items():
            if alias not in prepared:
                continue

            if target not in prepared:
                prepared[target] = prepared[alias]

            prepared.pop(alias, None)

        return prepared


    # Подготовить JSON-полезную нагрузку: тип, связи и встроенные модели
    def __prepare_payload(self, entity_type: str, payload: dict) -> dict:

        prepared = self.__apply_aliases(payload)
        prepared["$type"] = self._MODELS[entity_type].__name__

        for field, relation in self._RELATIONS.get(entity_type, {}).items():
            if field in prepared:
                prepared[field] = self.__prepare_relation(prepared[field], relation)

        return prepared


    # Подготовить значение связи (ссылка на существующую или встроенная модель)
    def __prepare_relation(self, value: object, relation: tuple) -> object:

        ref_type, is_list, embedded = relation

        if is_list:
            if value is None:
                return []

            if not isinstance(value, list):
                raise arguments_exception(
                    "payload", "Ожидался список связанных сущностей"
                )

            return [
                self.__prepare_relation_value(item, ref_type, embedded)
                for item in value
            ]

        return self.__prepare_relation_value(value, ref_type, embedded)


    # Подготовить одно значение связи
    def __prepare_relation_value(self, value: object, ref_type: str, embedded: bool) -> object:

        if value is None:
            return None

        if embedded:
            return self.__prepare_embedded(value, ref_type)

        reference = self._find(ref_type, self.__extract_id(value))
        if reference is None:
            raise arguments_exception(
                ref_type,
                f"Связанная сущность типа '{ref_type}' не найдена",
            )

        return self.__serializer.convert(reference)


    # Подготовить встроенную (вложенную) модель, например позицию рецепта
    def __prepare_embedded(self, value: object, ref_type: str) -> dict:

        if not isinstance(value, dict):
            raise arguments_exception(
                "payload", "Встроенная сущность должна быть JSON-объектом"
            )

        prepared = self.__apply_aliases(value)
        model_type = self._EMBEDDED_MODELS.get(ref_type) or self._MODELS.get(ref_type)
        prepared["$type"] = model_type.__name__ if model_type else value.get("$type")

        for field, relation in self._RELATIONS.get(ref_type, {}).items():
            if field in prepared:
                prepared[field] = self.__prepare_relation(prepared[field], relation)

        return prepared


    # Связать восстановленные ссылки с реальными объектами хранилища
    def __rebind(self, entity_type: str, model: entity) -> None:

        if entity_type == "nomenclature":
            model.group = self.__require_reference("group", model.group)
            model.range = self.__require_reference("range", model.range)

        elif entity_type == "range":
            if model.base_range is not None:
                model.base_range = self.__require_reference("range", model.base_range)

        elif entity_type == "recipe":
            for item in model.items:
                self.__rebind_embedded("recipe_item", item)

            sub_recipes = list(model.sub_recipes)
            for sub_recipe in sub_recipes:
                model.remove_sub_recipe(sub_recipe)
            for sub_recipe in sub_recipes:
                model.add_sub_recipe(self.__require_reference("recipe", sub_recipe))

        elif entity_type == "recipe_item":
            self.__rebind_embedded("recipe_item", model)


    # Перепривязать ссылки встроенной модели (позиции рецепта)
    def __rebind_embedded(self, entity_type: str, model: entity) -> None:

        if getattr(model, "range", None) is not None:
            model.range = self.__require_reference("range", model.range)

        for item in getattr(model, "items", []):
            self.__rebind_embedded(entity_type, item)


    # Получить реальную сущность по восстановленной ссылке
    def __require_reference(self, ref_type: str, value: object) -> entity | None:

        if value is None:
            return None

        reference = self._find(ref_type, self.__extract_id(value))
        if reference is None:
            raise arguments_exception(
                ref_type,
                f"Связанная сущность типа '{ref_type}' не найдена",
            )

        return reference


    # Извлечь код сущности из ссылки в любом поддерживаемом представлении
    @staticmethod
    def __extract_id(value: object) -> str:

        if isinstance(value, dict):
            value = value.get("id")

        if isinstance(value, entity):
            value = value.id

        if value is None or str(value).strip() == "":
            raise arguments_exception(
                "id", "Для связи необходимо передать код существующей сущности"
            )

        return str(value)


    # Найти сущности, которые ссылаются на указанную сущность
    def _find_dependents(self, entity_type: str, entity: entity) -> list[tuple[str, entity]]:

        dependents = []
        target_id = str(entity.id)

        for candidate_type in self._MODELS:
            for candidate in self.__collection(candidate_type).values():

                if candidate is entity:
                    continue

                data = self.__serializer.convert(candidate)
                data.pop("id", None)

                if self.__contains_id(data, target_id):
                    dependents.append((candidate_type, candidate))

        return dependents


    # Рекурсивно проверить наличие кода сущности внутри JSON-структуры
    @classmethod
    def __contains_id(cls, data: object, target_id: str) -> bool:

        if isinstance(data, dict):
            if "id" in data and str(data.get("id")) == target_id:
                return True
            return any(cls.__contains_id(value, target_id) for value in data.values())

        if isinstance(data, list):
            return any(cls.__contains_id(value, target_id) for value in data)

        return False


    # Человекочитаемое описание зависимостей
    @staticmethod
    def __format_dependents(dependents: list[tuple[str, entity]]) -> str:

        return ", ".join(
            f"{entity_type}:{candidate.name} ({candidate.id})"
            for entity_type, candidate in dependents
        )


    # Нормализация строки типа сущности
    @staticmethod
    def _normalize(entity_type: str) -> str:

        return (entity_type or "").strip().lower()


EntityService = entity_service
