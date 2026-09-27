from Src.Core.abstract_model import name_id
from Src.Core.exception import argument_exception


"""Модель склада"""    
class storage_model(name_id):
    
 
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
            raise argument_exception("address", "adress must be str")

        self.__address = value.strip()