from Src.Logics.deserialize_factory import deserialize_factory


class deserialize_service:
    """
    Оркестратор десериализации: делегирует работу универсальной фабрике.
    """


    __factory: deserialize_factory


    """Конструктор: использует переданную фабрику или создаёт свою"""
    def __init__(self, factory: deserialize_factory = None):

        self.__factory = factory if factory is not None else deserialize_factory()


    """Типы моделей, доступные общему механизму десериализации"""
    @property
    def model_types(self) -> list:

        return self.__factory.model_types


    """Восстановить объект из JSON-совместимых данных"""
    def deserialize(self, source: object):

        return self.__factory.convert(source)


DeserializeService = deserialize_service
