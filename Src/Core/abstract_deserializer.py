from abc import ABC, abstractmethod


"""
Абстрактный класс для восстановления объектов из словаря полей
"""
class abstract_deserializer(ABC):
    """
    Базовый абстрактный класс десериализатора.
    """

    @staticmethod
    @abstractmethod
    def is_supported(data: object) -> bool:
        """
        Проверить, что данные относятся к поддерживаемому десериализатором типу.
        """
        pass


    @abstractmethod
    def deserialize(self, data: object) -> object:
        """
        Восстановить объект из словаря полей.
        """
        pass


AbstractDeserializer = abstract_deserializer
