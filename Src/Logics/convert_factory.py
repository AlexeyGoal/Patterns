from Src.Core.abstract_convertor import abstract_convertor, AbstractConvertor
from Src.Logics.basic_convertor import basic_convertor, BasicConvertor
from Src.Logics.datetime_convertor import datetime_convertor, DatetimeConvertor
from Src.Logics.reference_convertor import reference_convertor, ReferenceConvertor


"""
Фабрика конвертеров
"""
class convert_factory:
    """Фабрика конверторов: подбирает и создаёт конверторы под значение"""

   
    """Зарегистрированные классы конверторов"""
    __convertor_types: list[type[AbstractConvertor]]


    """Конструктор: регистрирует классы конверторов простых типов, дат и ссылок."""
    def __init__(self):

        self.__convertor_types = [
            reference_convertor,
            datetime_convertor,
            basic_convertor,
        ]


    """
    Возвращает список созданных конверторов, поддерживающих значение.
    """
    def resolve(self, source: object) -> list[AbstractConvertor]:

        return [
            convertor_type()
            for convertor_type in self.__convertor_types
            if convertor_type.is_supported(source)
        ]


ConvertFactory = convert_factory
