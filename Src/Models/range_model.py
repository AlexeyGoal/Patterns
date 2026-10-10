from Src.Core.entity import entity
from Src.Core.exception import arguments_exception

"""Модель единицы измерения"""
class range_model(entity):

    """Конструктор единицы измерения"""
    def __init__(self, name="", conversion_factor=1, base_range=None):

        super().__init__()
        self.name = name
        self.conversion_factor = conversion_factor
        self.base_range = base_range


    """Геттер коэффициента пересчёта"""
    @property
    def conversion_factor(self):
        return self.__conversion_factor


    """Сеттер коэффициента пересчёта"""
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


    """Фабричный метод - создать килограмм"""
    @staticmethod
    def create_kilogram(name: str = "килограмм", base_name: str = "грамм"):
        gram = range_model(base_name, 1)
        return range_model(name, 1000, gram)


    """Фабричный метод - создать грамм"""
    @staticmethod
    def create_gram(name: str = "грамм"):
        return range_model(name, 1)


    """Фабричный метод - создать миллилитр"""
    @staticmethod
    def create_milliliter(name: str = "миллилитр"):
        return range_model(name, 1)


    """Фабричный метод - создать литр с базовой единицей миллилитр"""
    @staticmethod
    def create_liter(name: str = "литр", base_name: str = "миллилитр"):
        ml = range_model.create_milliliter(base_name)
        return range_model(name, 1000, ml)


    """Фабричный метод - создать штуку"""
    @staticmethod
    def create_piece(name: str = "штука"):
        return range_model(name, 1)
