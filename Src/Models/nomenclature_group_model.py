
from Src.Core.entity import entity
"""Модель группы номенклатуры"""
class nomenclature_group_model(entity):
 
    """Конструктор группы номенклатуры"""
    
    def __init__(self, name=""):
    
        super().__init__()
        self.name = name