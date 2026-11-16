from typing import Callable

from Src.Core.entity import entity
from Src.Core.exception import arguments_exception
from Src.Logics.deserialize_service import deserialize_service
from Src.Logics.entity_registry import entity_metadata_registry, entity_relation
from Src.Logics.serialize_factory import serialize_factory


"""
Преобразование JSON-представления доменной сущности и обратно.
"""
class entity_mapper:

    def __init__(
        self,
        registry: entity_metadata_registry,
        serializer: serialize_factory,
        deserializer: deserialize_service,
        finder: Callable[[str, str], entity | None],
    ):

        self.__registry = registry
        self.__serializer = serializer
        self.__deserializer = deserializer
        self.__finder = finder


    # Привести псевдонимы полей входного JSON к каноническим именам
    @classmethod
    def apply_aliases(
        cls,
        payload: dict,
        aliases: dict[str, str] = None,
    ) -> dict:

        prepared = dict(payload)
        aliases = entity.FIELD_ALIASES if aliases is None else aliases

        for alias, target in aliases.items():
            if alias not in prepared:
                continue

            if target not in prepared:
                prepared[target] = prepared[alias]

            prepared.pop(alias, None)

        return prepared


    # Сериализовать модель для последующего изменения
    def serialize(self, item: entity) -> dict:

        return self.__serializer.convert(item)


    # Наложить изменения на текущее состояние сущности
    def merge(self, existing: entity, payload: dict) -> dict:

        data = self.serialize(existing)
        aliases = self.__registry.aliases_by_model(type(existing))
        changes = self.apply_aliases(payload, aliases)

        for field, value in changes.items():
            data[field] = value

        return data


    # JSON-представление сущности с дополнительным алиасом кода
    def to_dto(self, item: entity) -> dict:

        data = self.__serializer.convert(item)

        if isinstance(data, dict):
            data.setdefault("code", data.get("id"))

        return data


    # Подготовить JSON-полезную нагрузку: тип, связи и встроенные модели
    def prepare(self, entity_type: str, payload: dict) -> dict:

        metadata = self.__registry.get(entity_type)
        aliases = (
            self.__registry.aliases_by_model(metadata.model)
            if metadata is not None
            else entity.FIELD_ALIASES
        )
        prepared = self.apply_aliases(payload, aliases)

        if metadata is None:
            return prepared

        prepared["$type"] = metadata.model.__name__

        for field, relation in metadata.relations.items():
            if field in prepared:
                prepared[field] = self.__prepare_relation(prepared[field], relation)

        return prepared


    # Восстановить модель и связать ссылки с реальным хранилищем
    def restore(self, entity_type: str, prepared: dict) -> entity:

        restored = self.__deserializer.deserialize(prepared)
        metadata = self.__registry.get(entity_type)
        model_type = metadata.model if metadata is not None else None

        if model_type is None or not isinstance(restored, model_type):
            raise arguments_exception(
                "payload",
                f"Не удалось создать сущность типа '{entity_type}'",
            )

        self.__rebind_model(restored)
        self.__validate(restored)
        return restored


    # Подготовить значение связи (ссылка на существующую или встроенная модель)
    def __prepare_relation(self, value: object, relation: entity_relation) -> object:

        if relation.is_list:
            if value is None:
                return []

            if not isinstance(value, list):
                raise arguments_exception(
                    "payload", "Ожидался список связанных сущностей"
                )

            return [
                self.__prepare_relation_value(item, relation)
                for item in value
            ]

        return self.__prepare_relation_value(value, relation)


    # Подготовить одно значение связи
    def __prepare_relation_value(self, value: object, relation: entity_relation) -> object:

        if value is None:
            return None

        if relation.embedded:
            return self.__prepare_embedded(value, relation.target)

        reference_type = self.__registry.api_type(relation.target)

        if reference_type is None:
            raise arguments_exception(
                "payload",
                f"Для модели '{relation.target.__name__}' не задан тип сущности API",
            )

        reference = self.__finder(reference_type, self.__extract_id(value))
        if reference is None:
            raise arguments_exception(
                reference_type,
                f"Связанная сущность типа '{reference_type}' не найдена",
            )

        return self.__serializer.convert(reference)


    # Подготовить встроенную (вложенную) модель, например позицию рецепта
    def __prepare_embedded(self, value: object, model_type: type[entity]) -> dict:

        if not isinstance(value, dict):
            raise arguments_exception(
                "payload", "Встроенная сущность должна быть JSON-объектом"
            )

        metadata = self.__registry.get_by_model(model_type)
        aliases = self.__registry.aliases_by_model(model_type)
        prepared = self.apply_aliases(value, aliases)
        prepared["$type"] = model_type.__name__

        if metadata is None:
            return prepared

        for field, relation in metadata.relations.items():
            if field in prepared:
                prepared[field] = self.__prepare_relation(prepared[field], relation)

        return prepared


    # Связать восстановленные ссылки с реальными объектами хранилища
    def __rebind_model(self, model: entity) -> None:

        metadata = self.__registry.get_by_model(type(model))

        if metadata is None:
            return

        for field, relation in metadata.relations.items():

            if not hasattr(model, field):
                continue

            value = getattr(model, field)

            if relation.is_list:
                self.__rebind_collection(model, field, relation, value)
            elif value is not None:
                if relation.embedded:
                    self.__rebind_model(value)
                else:
                    setattr(model, field, self.__require_reference(relation.target, value))


    # Перепривязать элементы коллекции модели
    def __rebind_collection(
        self,
        model: entity,
        field: str,
        relation: entity_relation,
        value: object,
    ) -> None:

        values = list(value or [])

        if relation.embedded:
            for item in values:
                if isinstance(item, entity):
                    self.__rebind_model(item)
            return

        rebound = [
            self.__require_reference(relation.target, item)
            for item in values
        ]
        self.__replace_collection(model, field, rebound)


    # Заменить элементы коллекции через сеттер или add_*/remove_*
    def __replace_collection(
        self,
        model: entity,
        field: str,
        values: list[entity],
    ) -> None:

        attribute = getattr(type(model), field, None)

        if isinstance(attribute, property) and attribute.fset is not None:
            setattr(model, field, values)
            return

        adder_name = self.__find_adder(type(model), field)

        if adder_name is None:
            raise arguments_exception(
                field,
                f"Для коллекции '{field}' не найден метод добавления элементов",
            )

        remover_name = adder_name.replace("add_", "remove_", 1)
        remover = getattr(model, remover_name, None)

        if callable(remover):
            for item in list(getattr(model, field)):
                remover(item)

        adder = getattr(model, adder_name)

        for item in values:
            adder(item)


    # Получить реальную сущность по восстановленной ссылке
    def __require_reference(self, ref_type: type[entity], value: object) -> entity | None:

        if value is None:
            return None

        entity_type = self.__registry.api_type(ref_type)

        if entity_type is None:
            raise arguments_exception(
                ref_type.__name__,
                f"Для модели '{ref_type.__name__}' не задан тип сущности API",
            )

        reference = self.__finder(entity_type, self.__extract_id(value))
        if reference is None:
            raise arguments_exception(
                entity_type,
                f"Связанная сущность типа '{entity_type}' не найдена",
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


    # Дополнительные проверки корректности доменной модели
    def __validate(self, model: entity) -> None:

        metadata = self.__registry.get_by_model(type(model))

        if metadata is None:
            return

        for field, relation in metadata.relations.items():

            if relation.is_list or relation.target is not type(model):
                continue

            visited = {str(model.id)}
            current = getattr(model, field, None)

            while current is not None:
                current_id = str(getattr(current, "id", ""))

                if current_id in visited:
                    raise arguments_exception(
                        field,
                        f"Обнаружена циклическая ссылка в поле '{field}'",
                    )

                visited.add(current_id)
                current = getattr(current, field, None)


    # Найти метод add_* для свойства-коллекции
    @staticmethod
    def __find_adder(model_type: type[entity], property_name: str) -> str | None:

        methods = {
            name
            for name in dir(model_type)
            if name.startswith("add_")
        }

        candidates = [f"add_{property_name}"]

        if property_name.endswith("ies"):
            candidates.append(f"add_{property_name[:-3]}y")

        if property_name.endswith("es"):
            candidates.append(f"add_{property_name[:-2]}")

        if property_name.endswith("s"):
            candidates.append(f"add_{property_name[:-1]}")

        for candidate in candidates:
            if candidate in methods:
                return candidate

        return None


EntityMapper = entity_mapper
