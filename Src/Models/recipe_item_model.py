from Src.Core.entity import entity
from Src.Core.exception import arguments_exception
from Src.Models.range_model import range_model


class recipe_item_type:
    """Тypes позиций рецепта"""
    INGREDIENT = "ingredient"
    SEMI_FINISHED = "semi_finished"
    PACKAGING = "packaging"


"""Модель позиции рецепта (ингредиент, полуфабрикат или упаковка)"""
class recipe_item_model(entity):

    """Конструктор позиции рецепта"""
    def __init__(self, name="", weight=0.0, range=None, item_type=recipe_item_type.INGREDIENT):

        super().__init__()
        self.name = name
        self.weight = weight
        self.range = range
        self.type = item_type
        self.__items = []


    """Геттер веса"""
    @property
    def weight(self):
        return self.__weight


    """Сеттер веса"""
    @weight.setter
    def weight(self, value):

        if not isinstance(value, (int, float)):
            raise arguments_exception("weight", "weight must be int or float")

        if value < 0:
            raise arguments_exception("weight", "weight must be greater than or equal to 0")

        self.__weight = float(value)


    """Геттер единицы измерения"""
    @property
    def range(self):
        return self.__range


    """Сеттер единицы измерения"""
    @range.setter
    def range(self, value):

        if value is not None and not isinstance(value, range_model):
            raise arguments_exception("range", "range should be of the type range_model")

        self.__range = value


    """Геттер типа позиции"""
    @property
    def type(self):
        return self.__type


    """Сеттер типа позиции"""
    @type.setter
    def type(self, value):

        valid_types = (recipe_item_type.INGREDIENT, recipe_item_type.SEMI_FINISHED, recipe_item_type.PACKAGING)

        if value not in valid_types:
            raise arguments_exception("type", f"type must be one of: {valid_types}")

        self.__type = value


    """Геттер списка вложенных позиций"""
    @property
    def items(self):
        return list(self.__items)


    """Добавление вложенной позиции"""
    def add_item(self, item):

        if not isinstance(item, recipe_item_model):
            raise arguments_exception("item", "item should be of the type recipe_item_model")

        self.__items.append(item)


    """Удаление вложенной позиции"""
    def remove_item(self, item):

        if item in self.__items:
            self.__items.remove(item)


    """Рекурсивный расчёт веса позиции"""
    def calculate_weight(self):

        if self.type == recipe_item_type.INGREDIENT or self.type == recipe_item_type.PACKAGING:
            return self.weight

        total = 0.0
        for item in self.__items:
            total += item.calculate_weight()

        return total


    """Фабричный метод - создать ингредиент"""
    @staticmethod
    def create_ingredient(name="", weight=0.0, range=None):
        return recipe_item_model(name, weight, range, recipe_item_type.INGREDIENT)


    """Фабричный метод - создать полуфабрикат"""
    @staticmethod
    def create_semi_finished(name="", weight=0.0, range=None):
        return recipe_item_model(name, weight, range, recipe_item_type.SEMI_FINISHED)


    """Фабричный метод - создать упаковку"""
    @staticmethod
    def create_packaging(name="", weight=0.0, range=None):
        return recipe_item_model(name, weight, range, recipe_item_type.PACKAGING)
