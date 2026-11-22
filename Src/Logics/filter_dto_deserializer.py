from Src.Core.exception import arguments_exception
from Src.Core.filter_type import filter_type as filter_type_enum
from Src.Dtos.filter_dto import filter_dto
from Src.Logics.deserialize_factory import deserialize_factory
from Src.Logics.deserialize_service import deserialize_service


"""
Десериализация DTO фильтрации из JSON-совместимого словаря.

Использует общий механизм десериализации: на вход подаётся словарь, на выходе
получается готовый объект filter_dto. Дополнительно приводятся псевдонимы полей
и строковые значения перечисления filter_type.
"""
class filter_dto_deserializer:

    """Маркер типа модели для механизма десериализации"""
    TYPE_FIELD = "$type"

    """Конструктор десериализатора"""
    def __init__(self, service: deserialize_service = None):

        if service is None:
            model_types = [
                *deserialize_factory().model_types,
                filter_dto,
            ]
            service = deserialize_service(deserialize_factory(model_types))

        self.__service = service

    """Восстановить DTO фильтрации из словаря"""
    def deserialize(
        self,
        payload: dict,
        entity_type: str = None,
    ) -> filter_dto:

        if not isinstance(payload, dict):
            raise arguments_exception(
                "payload",
                "Тело запроса должно быть JSON-объектом",
            )

        prepared = self.__apply_aliases(payload)

        if entity_type is not None:
            prepared["entity_type"] = entity_type

        prepared["filter_type"] = self.__normalize_filter_type(
            prepared.get("filter_type")
        )
        prepared[self.TYPE_FIELD] = filter_dto.__name__

        result = self.__service.deserialize(prepared)

        if not isinstance(result, filter_dto):
            raise arguments_exception(
                "payload",
                "Не удалось восстановить DTO фильтрации",
            )

        return result

    """Привести псевдонимы полей DTO к каноническим именам"""
    @staticmethod
    def __apply_aliases(payload: dict) -> dict:

        result = dict(payload)

        for alias, target in filter_dto.FIELD_ALIASES.items():
            if alias not in result:
                continue

            if target not in result:
                result[target] = result[alias]

            result.pop(alias, None)

        return result

    """Привести вариант фильтрации к перечислению filter_type"""
    @staticmethod
    def __normalize_filter_type(value: object) -> filter_type_enum:

        if value is None:
            return filter_type_enum.EQUALS

        if isinstance(value, filter_type_enum):
            return value

        if isinstance(value, str):
            normalized = value.strip().upper()
            parsed = filter_type_enum.__members__.get(normalized)

            if parsed is not None:
                return parsed

            raise arguments_exception(
                "filter_type",
                f"Неподдерживаемый вариант фильтрации: '{value}'. "
                f"Допустимые значения: {', '.join(filter_type_enum.__members__)}",
            )

        raise arguments_exception(
            "filter_type",
            f"Ожидался вариант фильтрации {filter_type_enum.__name__}",
        )


FilterDtoDeserializer = filter_dto_deserializer
