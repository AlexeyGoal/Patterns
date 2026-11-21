from Src.Core.exception import arguments_exception
from Src.Dtos.filter_dto import filter_dto
from Src.Logics.entity_filter import entity_filter


"""
Прототип фильтрации доменных сущностей.

Один и тот же прототип используется для всех доменных моделей. Конкретная
модель, поле и значение задаются DTO, а метод clone() создаёт копию прототипа
с нужной настройкой фильтрации.
"""
class filter_prototype:

    """Конструктор прототипа фильтрации."""
    def __init__(self, query: filter_dto = None, filter_logic: entity_filter = None):

        if query is not None and not isinstance(query, filter_dto):
            raise arguments_exception("query", "Ожидался DTO фильтрации")

        self.__query = query
        self.__filter = filter_logic if filter_logic is not None else entity_filter()

    """DTO, которым настроен прототип."""
    @property
    def query(self) -> filter_dto | None:
        return self.__query

    """Создать копию прототипа, при необходимости с другим DTO."""
    def clone(self, query: filter_dto = None) -> "filter_prototype":

        if query is not None and not isinstance(query, filter_dto):
            raise arguments_exception("query", "Ожидался DTO фильтрации")

        return type(self)(
            query if query is not None else self.__query,
            self.__filter,
        )

    """Проверить поле модели и вернуть его фактическое имя."""
    def resolve_field(self, model_type: type, field_name: str) -> str:

        return self.__filter.resolve_field(model_type, field_name)

    """Отфильтровать коллекцию доменных сущностей."""
    def filter(self, items: list) -> list:

        if self.__query is None:
            raise arguments_exception(
                "query",
                "Прототип не настроен DTO фильтрации",
            )

        return self.__filter.apply(items, self.__query)


FilterPrototype = filter_prototype
