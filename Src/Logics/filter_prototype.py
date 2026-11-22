from Src.Core.exception import arguments_exception
from Src.Dtos.filter_dto import filter_dto
from Src.Logics.entity_filter import entity_filter


"""
Прототип фильтрации доменных сущностей.
"""
class filter_prototype:

    """Конструктор прототипа фильтрации"""
    def __init__(
        self,
        items: list = None,
        query: filter_dto = None,
        filter_logic: entity_filter = None,
        source: object = None,
    ):

        if query is not None and not isinstance(query, filter_dto):
            raise arguments_exception("query", "Ожидался DTO фильтрации")

        self.__items = list(items) if items is not None else []
        self.__query = query
        self.__filter = filter_logic if filter_logic is not None else entity_filter()
        self.__source = source

    """Отфильтрованные данные прототипа"""
    @property
    def items(self) -> list:
        return list(self.__items)

    """DTO, которым настроен прототип"""
    @property
    def query(self) -> filter_dto | None:
        return self.__query

    """Создать клон прототипа с уже отфильтрованным списком"""
    def clone(self, query: filter_dto = None) -> "filter_prototype":

        selected = query if query is not None else self.__query

        if selected is None:
            raise arguments_exception(
                "query",
                "Прототип не настроен DTO фильтрации",
            )

        if not isinstance(selected, filter_dto):
            raise arguments_exception("query", "Ожидался DTO фильтрации")

        source_items = self.__source_items(selected)
        filtered = self.__filter.apply(source_items, selected)

        return type(self)(
            items=filtered,
            query=selected,
            filter_logic=self.__filter,
            source=self.__source,
        )

    """Проверить поле модели и вернуть его фактическое имя"""
    def resolve_field(self, model_type: type, field_name: str) -> str:

        return self.__filter.resolve_field(model_type, field_name)

    """Исходные данные для фильтрации"""
    def __source_items(self, query: filter_dto) -> list:

        if self.__source is None:
            return list(self.__items)

        if callable(self.__source):
            return list(self.__source(query.entity_type) or [])

        return list(self.__source)


FilterPrototype = filter_prototype
