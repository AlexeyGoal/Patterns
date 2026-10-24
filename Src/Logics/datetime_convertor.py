import datetime
from Src.Core.abstract_convertor import abstract_convertor, AbstractConvertor
from Src.Core.exception import arguments_exception


"""
Реализация конвертера для типа DateTime
"""
class datetime_convertor(abstract_convertor):
    """
    Конвертер значений типа DateTime в словарь полей.
    """

    """Тип значения, поддерживаемый конвертером"""
    __supported_types = (datetime.datetime,)


    """Проверить, что значение относится к типу DateTime"""
    @staticmethod
    def is_supported(source: object) -> bool:

        return isinstance(source, datetime_convertor.__supported_types)


    """
    Конвертировать значение типа DateTime в словарь полей.
    """
    def Convert(self, source: object) -> dict:

        if not self.is_supported(source):
            raise arguments_exception("source", "datetime_convertor supports only DateTime type")

        return {type(source).__name__: source}


DatetimeConvertor = datetime_convertor
