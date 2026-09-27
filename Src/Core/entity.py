from abc import ABC
import uuid
from Src.Core.exception import arguments_exception


"""Абстрактный класс для имени и id объекта"""
class entity(ABC):
    
    """Конструктор класса"""
    def __init__(self):
        self.__name = ""
        self.__id = uuid.uuid4()

    """Геттер для id"""
    @property
    def id(self):
        return self.__id

    """Сеттер для id"""
    @id.setter
    def id(self, value: uuid.UUID):
        if not isinstance(value, uuid.UUID):
            raise arguments_exception("value", "id must not be empty")
            
        self.__id = value

    """Геттер для name"""
    @property
    def name(self):
        return self.__name

    """Сеттер для name"""
    @name.setter
    def name(self, value: str):
       if value is None or value.strip() == "":
            raise arguments_exception("name", "name must not be empty")
        
       self.__name = value

        
    """Сравнение сущностей по идентификатору"""
    def __eq__(self, other):
        if not isinstance(other, entity):
            return NotImplemented
        return self.__id == other.__id
