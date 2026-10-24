from abc import ABC, abstractmethod


"""
Абстрактный класс для конвертации объекта в словарь полей
"""
class abstract_convertor(ABC):
    """
    Базовый абстрактный класс конвертера.
    """

    @abstractmethod
    def Convert(self, source: object) -> dict:
        """
        Конвертировать переданный объект в словарь полей.
        """
        pass


AbstractConvertor = abstract_convertor
