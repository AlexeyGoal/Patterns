from Src.Core.entity import entity
from Src.Core.exception import arguments_exception
from Src.Core.filter_type import filter_type as filter_type_enum


"""
DTO-модель с параметрами фильтрации доменной сущности.
"""
class filter_dto(entity):

    """Псевдонимы полей DTO фильтрации."""
    FIELD_ALIASES = {
        "entity": "entity_type",
        "field": "field_name",
    }

    """Конструктор DTO фильтрации."""
    def __init__(
        self,
        entity_type: str = "",
        field_name: str = "",
        value: object = "",
        filter_type: object = None,
    ):

        super().__init__()
        self.__entity_type = str(entity_type or "").strip().lower()
        self.__field_name = str(field_name or "").strip()
        self.__value = "" if value is None else str(value).strip()
        self.__filter_type = (
            filter_type if filter_type is not None else filter_type_enum.EQUALS
        )

        self.validate()

    """Тип доменной модели, по которой выполняется фильтрация."""
    @property
    def entity_type(self) -> str:
        return self.__entity_type

    """Имя поля фильтрации."""
    @property
    def field_name(self) -> str:
        return self.__field_name

    """Значение для сравнения."""
    @property
    def value(self) -> str:
        return self.__value

    """Вариант сравнения значений."""
    @property
    def filter_type(self) -> filter_type_enum:
        return self.__filter_type

    """Проверить обязательные параметры DTO."""
    def validate(self) -> "filter_dto":

        if self.__entity_type == "":
            raise arguments_exception(
                "entity_type",
                "Не задан тип доменной модели для фильтрации",
            )

        if self.__field_name == "":
            raise arguments_exception(
                "field_name",
                "Не задано имя поля фильтрации",
            )

        if self.__value == "":
            raise arguments_exception(
                self.__field_name,
                f"Не задано значение для фильтрации по полю '{self.__field_name}'",
            )

        if not isinstance(self.__filter_type, filter_type_enum):
            raise arguments_exception(
                "filter_type",
                f"Ожидался вариант фильтрации {filter_type_enum.__name__}",
            )

        return self