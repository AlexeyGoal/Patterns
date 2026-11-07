from Src.Logics.convert_factory import convert_factory, ConvertFactory


class convert_service:
    """
    Оркестратор: обходит структуру (списки и словари), просит у фабрики конверторы,
    мержит их результаты и рекурсивно обходит вложенные значения.
    """


    __factory: convert_factory


    """Конструктор: использует переданную фабрику или создаёт свою."""
    def __init__(self, factory: convert_factory = None):

        self.__factory = factory if factory is not None else convert_factory()


    """
    Превращает объект в словарь; списки и словари обходят рекурсивно.
    """
    def convert(self, source: object) -> dict | list:

        if isinstance(source, list):
            return [self.convert(item) for item in source]

        if isinstance(source, dict):
            return {key: self.convert(item) for key, item in source.items()}

        result = {}

        
        for convertor in self.__factory.resolve(source):
            for field, value in convertor.convert(source).items():
                result[field] = value

        return result


ConvertService = convert_service
