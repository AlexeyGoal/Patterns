from Src.Core.entity import entity
from Src.Core.exception import arguments_exception


"""Модель склада"""    
class storage_model(entity):
    
 
    """Конструктор склада"""
    def __init__(self, name="", address=""):
       
        super().__init__()
        self.name = name
        self.address = address

    """Геттер адреса склада"""
    @property
    def address(self):
        
        return self.__address

    """Сеттер адреса склада"""
    @address.setter
    def address(self, value):
        
        if not isinstance(value, str):
            raise arguments_exception("address", "adress must be str")

        self.__address = value.strip()