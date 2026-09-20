from abc import ABC
import uuid

"""Абстрактный класс для имени и id объекта"""
class entity(ABC):
    
    """Конструктор класса"""
    def __init__(self):
        self.__name = ""
        self.__id = uuid.uuid4()

    """Геттер для id"""
    @property
    def get_id(self):
        return self.__id

    """Геттер для name"""
    @property
    def name(self) -> str:
        return self.__name

    """Сеттер для name"""
    @name.setter
    def name(self, new_name: str):
        if new_name is not None and len(new_name) > 0:
            self.__name = new_name
        else:
            raise ValueError("Имя не должно быть пустым")