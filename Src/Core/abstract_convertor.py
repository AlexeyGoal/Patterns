from abc import ABC, abstractmethod


"""
Абстрактный класс для конвертации объекта в словарь полей
"""
class abstract_convertor(ABC):
    """
    Базовый абстрактный класс конвертера.
    """

    @staticmethod
    @abstractmethod
    def is_supported(source: object) -> bool:
        """
        Проверить, что объект относится к поддерживаемым конвертером типам.
        Часть контракта: по этому методу фабрика подбирает нужный конвертер.
        """
        pass

    @abstractmethod
    def convert(self, source: object) -> dict:
        """
        Конвертировать переданный объект в словарь полей.
        """
        pass


AbstractConvertor = abstract_convertor
