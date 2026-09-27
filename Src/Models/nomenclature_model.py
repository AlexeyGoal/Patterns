from Src.Core.entity import entity
from Src.Core.exception import arguments_exception, max_length_exception
from Src.Models.range_model import range_model
from Src.Models.nomenclature_group_model import nomenclature_group_model

"""Модель номенклатуры"""
class nomenclature_model(name_id):
    
    """Максимальная длина полного наименования"""
    __max_full_name_length = 255

    """Конструктор номенкалтуры"""
    def __init__(self, name="", full_name="", group=None, range=None):
        
        super().__init__()
        self.name = name
        self.full_name = full_name
        self.group = group
        self.range = range

    """Геттер полного наименования"""
    @property
    def full_name(self):
        
        return self.__full_name

    """Сеттер полного наименования"""
    @full_name.setter
    def full_name(self, value):
    
        if value is None or str(value).strip() == "":
            raise arguments_exception("full_name", "full_name must not be empty")

        value = str(value).strip()

        if len(value) > self.__max_full_name_length:
            raise max_length_exception("full_name", len(value), self.__max_full_name_length)

        self.__full_name = value

    """Геттер группы номенклатуры"""
    @property
    def group(self):
        return self.__group

    """Сеттер группы номенклатуры"""
    @group.setter
    def group(self, value):
        if not isinstance(value, nomenclature_group_model):
            raise argument_exception("group", "group should be of the type nomenclature_group_model")

        self.__group = value

    """Геттер единицы измерения номенклатуры"""
    @property
    def range(self):
        return self.__range

    """Cеттер единицы измерения номенклатуры"""
    @range.setter
    def range(self, value):
    
        if not isinstance(value, range_model):
            raise arguments_exception("range", "range should be of the type range_model")

        self.__range = value