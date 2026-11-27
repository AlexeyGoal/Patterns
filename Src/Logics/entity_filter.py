import inspect
import uuid

from Src.Core.entity import entity
from Src.Core.exception import arguments_exception
from Src.Core.filter_type import filter_type
from Src.Dtos.filter_dto import filter_dto


"""
Применение DTO фильтрации к коллекции доменных сущностей.
"""
class entity_filter:

    """Проверить, подходит ли сущность под условие DTO фильтрации."""
    def matches(self, item: entity, query: filter_dto) -> bool:

        if not isinstance(item, entity):
            raise arguments_exception("item", "Ожидалась доменная сущность")

        if not isinstance(query, filter_dto):
            raise arguments_exception("query", "Ожидался DTO фильтрации")

        # Проверяем, что поле существует у корневой модели, затем ищем
        # совпадение по самой сущности и по всем вложенным сущностям.
        self.resolve_field(type(item), query.field_name)

        return self.__matches_entity(
            item,
            query.field_name,
            query.value,
            query.filter_type,
            set(),
        )

    """Отфильтровать коллекцию сущностей по DTO."""
    def apply(self, items: list[entity], query: filter_dto) -> list[entity]:

        if query is None:
            raise arguments_exception("query", "Не задан DTO фильтрации")

        return [item for item in items if self.matches(item, query)]

    """Проверить поле модели и вернуть его фактическое имя."""
    def resolve_field(self, model_type: type[entity], field_name: str) -> str:

        if not isinstance(model_type, type) or not issubclass(model_type, entity):
            raise arguments_exception("model_type", "Ожидался класс доменной модели")

        name = str(field_name or "").strip()

        if name == "":
            raise arguments_exception("field_name", "Не задано имя поля фильтрации")

        resolved = self.__aliases_by_model(model_type).get(name, name)

        if self.__has_field(model_type, resolved):
            return resolved

        raise arguments_exception(
            "field_name",
            f"Поле '{field_name}' отсутствует у модели '{model_type.__name__}'",
        )

    """Рекурсивно проверить сущность и её вложенные структуры."""
    def __matches_entity(
        self,
        item: entity,
        field_name: str,
        expected: str,
        mode: filter_type,
        visited: set[int],
    ) -> bool:

        marker = id(item)

        if marker in visited:
            return False

        visited.add(marker)

        for value in self.__local_values(item, field_name):
            if self.__compare(value, expected, mode):
                return True

        for related in self.__related_entities(item):
            if self.__matches_entity(related, field_name, expected, mode, visited):
                return True

        return False

    """Значения поля у текущей сущности без поиска в связях."""
    def __local_values(self, item: entity, field_name: str) -> list[str]:

        resolved = self.__aliases_by_model(type(item)).get(field_name, field_name)

        if not self.__has_field(type(item), resolved):
            return []

        return self.__flatten(getattr(item, resolved, None))

    """Привести значение поля к набору строк для сравнения."""
    def __flatten(self, value: object) -> list[str]:

        if value is None:
            return []

        if isinstance(value, uuid.UUID):
            return [str(value)]

        if isinstance(value, entity):
            return [
                str(getattr(value, "name", "")),
                str(value.id),
            ]

        if isinstance(value, (list, tuple, set)):
            result = []

            for element in value:
                result.extend(self.__flatten(element))

            return result

        if isinstance(value, dict):
            result = []

            for element in value.values():
                result.extend(self.__flatten(element))

            return result

        return [str(value)]

    """Получить вложенные доменные сущности текущей сущности."""
    def __related_entities(self, item: entity) -> list[entity]:

        result = []

        for name in dir(type(item)):

            if name.startswith("_"):
                continue

            attribute = getattr(type(item), name, None)

            if not isinstance(attribute, property):
                continue

            try:
                value = getattr(item, name)
            except Exception:
                continue

            result.extend(self.__extract_entities(value))

        for name, value in vars(item).items():

            if name.startswith("_"):
                continue

            result.extend(self.__extract_entities(value))

        return result

    """Извлечь сущности из значения поля."""
    def __extract_entities(self, value: object) -> list[entity]:

        if isinstance(value, entity):
            return [value]

        if isinstance(value, (list, tuple, set)):
            result = []

            for element in value:
                result.extend(self.__extract_entities(element))

            return result

        if isinstance(value, dict):
            result = []

            for element in value.values():
                result.extend(self.__extract_entities(element))

            return result

        return []

    """Псевдонимы полей, объявленные моделью и её базовыми классами."""
    @staticmethod
    def __aliases_by_model(model_type: type[entity]) -> dict[str, str]:

        result = {}

        for base in reversed(model_type.__mro__):
            declared = base.__dict__.get("FIELD_ALIASES")

            if not isinstance(declared, dict):
                continue

            for alias, target in declared.items():
                if isinstance(alias, str) and isinstance(target, str):
                    result[alias.strip()] = target.strip()

        return result

    """Проверить, что у модели есть публичное поле."""
    @staticmethod
    def __has_field(model_type: type[entity], field_name: str) -> bool:

        attribute = getattr(model_type, field_name, None)

        if isinstance(attribute, property):
            return True

        if field_name in getattr(model_type, "__annotations__", {}):
            return True

        try:
            parameters = inspect.signature(model_type).parameters
        except (TypeError, ValueError):
            parameters = {}

        return field_name in parameters

    """Сравнить фактическое значение с ожидаемым по варианту фильтрации."""
    @staticmethod
    def __compare(actual: str, expected: str, mode: filter_type) -> bool:

        actual_value = actual.strip()
        expected_value = expected.strip()

        if mode == filter_type.EQUALS:
            return actual_value.casefold() == expected_value.casefold()

        if mode == filter_type.LIKE:
            return expected_value.casefold() in actual_value.casefold()

        raise arguments_exception(
            "filter_type",
            f"Неподдерживаемый вариант фильтрации: '{mode}'",
        )
