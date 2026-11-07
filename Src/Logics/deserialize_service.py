from Src.Logics.deserialize_factory import deserialize_factory, DeserializeFactory


class deserialize_service:
    """
    Оркестратор десериализации: рекурсивно обходит списки и словари,
    просит у фабрики подходящий десериализатор и восстанавливает модели.
    """


    __factory: deserialize_factory


    """Конструктор: использует переданную фабрику или создаёт свою"""
    def __init__(self, factory: deserialize_factory = None):

        self.__factory = factory if factory is not None else deserialize_factory()


    """
    Восстанавливает объект из словаря; списки и словари обходит рекурсивно.
    """
    def deserialize(self, source: object):

        if isinstance(source, list):
            return [self.deserialize(item) for item in source]

        if isinstance(source, dict):

            for deserializer in self.__factory.resolve(source):

                
                if hasattr(deserializer, "bind"):
                    deserializer.bind(self)

                return deserializer.deserialize(source)

           
            return {key: self.deserialize(value) for key, value in source.items()}

        
        return source


DeserializeService = deserialize_service
