from abc import ABC
import uuid
from Src.Core.exception import arguments_exception, max_length_exception


"""Абстрактный класс для имени и id объекта"""
class entity(ABC):

    __max_name_length = 50
    
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
        
        new_name = value.strip()

        if len(new_name) > self.__max_name_length:
            raise max_length_exception("name", len(value), self.__max_name_length)

        self.__name = new_name

        
    """Сравнение сущностей по идентификатору"""
    def __eq__(self, other):
        if not isinstance(other, entity):
            return NotImplemented
        return self.__id == other.__id
