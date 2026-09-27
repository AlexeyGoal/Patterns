from Src.Core.entity import entity
from Src.Core.exception import arguments_exception

""" Модель единицa измерения"""
class range_model(entity):
    
     
    """Конструктор единицы измерения"""
    def __init__(self, name="", conversion_factor=1, base_range=None):
       
        super().__init__()
        self.name = name
        self.conversion_factor = conversion_factor
        self.base_range = base_range


    
    """ Геттер коэффицента пересчета """    
    @property
    def conversion_factor(self):

        return self.__conversion_factor


    """Сеттер коэфицента пересчета"""
    @conversion_factor.setter
    def conversion_factor(self, value):
        
        if not isinstance(value, (int, float)):
            raise arguments_exception("conversion_factor", "conversion_factor must be int or float")

        if value <= 0:
            raise arguments_exception("conversion_factor", "conversion_factor must be greater than 0")

        self.__conversion_factor = value

    
    """Геттер базовой единицы измерения"""
    @property
    def base_range(self):
        return self.__base_range

    """Сеттер базовой единицы"""
    @base_range.setter
    def base_range(self, value):
       
        if value is not None and not isinstance(value, range_model):
            raise arguments_exception("base_range", "base_range should be of the type range_model")

        self.__base_range = value

    