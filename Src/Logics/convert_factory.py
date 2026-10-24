from Src.Core.entity import entity
from Src.Logics.basic_convertor import basic_convertor, BasicConvertor
from Src.Logics.datetime_convertor import datetime_convertor, DatetimeConvertor
from Src.Logics.reference_convertor import reference_convertor, ReferenceConvertor


"""
Фабрика конвертеров
"""
class convert_factory:
    """
    Фабрика конвертеров: принимает любой объект любого типа.
    """

    """Конструктор фабрики - регистрация конвертеров в порядке приоритета подбора"""
    def __init__(self):

        self.__convertors = [
            reference_convertor(),
            datetime_convertor(),
            basic_convertor(),
        ]


    """
    Превращает объект в словарь, список - в список словарей.
    """
    def convert(self, source: object) -> dict | list:

        
        if isinstance(source, list):
            return [self.convert(item) for item in source]

        result = {}

        for convertor in self.__convertors:
            if convertor.is_supported(source):
                for field, value in convertor.Convert(source).items():
                    result[field] = value


        for field, value in list(result.items()):
            if isinstance(value, list):
                result[field] = self.convert(value)

        return result


ConvertFactory = convert_factory
