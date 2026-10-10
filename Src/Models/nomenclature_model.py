from Src.Core.entity import entity
from Src.Core.exception import arguments_exception, max_length_exception
from Src.Models.range_model import range_model
from Src.Models.nomenclature_group_model import nomenclature_group_model

"""Модель номенклатуры"""
class nomenclature_model(entity):
    
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
            raise arguments_exception("group", "group should be of the type nomenclature_group_model")

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


    @staticmethod
    def create_flour(group=None, range=None):
        """
        Фабричный метод - создать номенклатуру "Мука пшеничная".

        Параметры:
            group: Группа номенклатуры (по умолчанию - "Бакалея")
            range: Единица измерения (по умолчанию - килограмм)
        """
        group = group or nomenclature_group_model.create_grocery()
        range = range or range_model.create_kilogram()
        return nomenclature_model("Мука пшеничная", "Мука пшеничная высший сорт", group, range)

    @staticmethod
    def create_milk(group=None, range=None):
        """
        Фабричный метод - создать номенклатуру "Молоко 3.2%".

        Параметры:
            group: Группа номенклатуры (по умолчанию - "Молочные продукты")
            range: Единица измерения (по умолчанию - литр)
        """
        group = group or nomenclature_group_model.create_dairy()
        range = range or range_model.create_liter()
        return nomenclature_model("Молоко 3.2%", "Молоко коровье пастеризованное 3.2%", group, range)

    @staticmethod
    def create_eggs(group=None, range=None):
        """
        Фабричный метод - создать номенклатуру "Яйца куриные".

        Параметры:
            group: Группа номенклатуры (по умолчанию - "Молочные продукты")
            range: Единица измерения (по умолчанию - штука)
        """
        group = group or nomenclature_group_model.create_dairy()
        range = range or range_model.create_piece()
        return nomenclature_model("Яйца куриные", "Яйца куриные столовые С0", group, range)

    @staticmethod
    def create_butter(group=None, range=None):
        """
        Фабричный метод - создать номенклатуру "Масло сливочное".

        Параметры:
            group: Группа номенклатуры (по умолчанию - "Молочные продукты")
            range: Единица измерения (по умолчанию - килограмм)
        """
        group = group or nomenclature_group_model.create_dairy()
        range = range or range_model.create_kilogram()
        return nomenclature_model("Масло сливочное", "Масло сливочное крестьянское 72.5%", group, range)

    @staticmethod
    def create_sugar(group=None, range=None):
        """
        Фабричный метод - создать номенклатуру "Сахар".

        Параметры:
            group: Группа номенклатуры (по умолчанию - "Бакалея")
            range: Единица измерения (по умолчанию - килограмм)
        """
        group = group or nomenclature_group_model.create_grocery()
        range = range or range_model.create_kilogram()
        return nomenclature_model("Сахар", "Сахар белый кристаллический", group, range)

    @staticmethod
    def create_salt(group=None, range=None):
        """
        Фабричный метод - создать номенклатуру "Соль".

        Параметры:
            group: Группа номенклатуры (по умолчанию - "Бакалея")
            range: Единица измерения (по умолчанию - килограмм)
        """
        group = group or nomenclature_group_model.create_grocery()
        range = range or range_model.create_kilogram()
        return nomenclature_model("Соль", "Соль поваренная пищевая", group, range)

    @staticmethod
    def create_cottage_cheese(group=None, range=None):
        """
        Фабричный метод - создать номенклатуру "Творог 9%".

        Параметры:
            group: Группа номенклатуры (по умолчанию - "Молочные продукты")
            range: Единица измерения (по умолчанию - килограмм)
        """
        group = group or nomenclature_group_model.create_dairy()
        range = range or range_model.create_kilogram()
        return nomenclature_model("Творог 9%", "Творог 9% протёртый", group, range)

    @staticmethod
    def create_sunflower_oil(group=None, range=None):
        """
        Фабричный метод - создать номенклатуру "Масло подсолнечное".

        Параметры:
            group: Группа номенклатуры (по умолчанию - "Бакалея")
            range: Единица измерения (по умолчанию - литр)
        """
        group = group or nomenclature_group_model.create_grocery()
        range = range or range_model.create_liter()
        return nomenclature_model("Масло подсолнечное", "Масло подсолнечное рафинированное", group, range)

    @staticmethod
    def create_breakfast_box(group=None, range=None):
        """
        Фабричный метод - создать номенклатуру "Коробка для завтраков".

        Параметры:
            group: Группа номенклатуры (по умолчанию - "Упаковка")
            range: Единица измерения (по умолчанию - штука)
        """
        group = group or nomenclature_group_model.create_packaging()
        range = range or range_model.create_piece()
        return nomenclature_model("Коробка для завтраков", "Коробка бумажная для завтраков", group, range)

    """Фабричный метод - создать номенклатуру "Суп-лапша домашняя" """
    @staticmethod
    def create_dish_noodle_soup(group=None, range=None):
        group = group or nomenclature_group_model.create_dishes()
        range = range or range_model.create_piece()
        return nomenclature_model("Суп-лапша домашняя", "Суп-лапша домашняя в порционной тарелке", group, range)


    """Фабричный метод - создать номенклатуру "Курица (тушка)" """
    @staticmethod
    def create_chicken(group=None, range=None):
        group = group or nomenclature_group_model.create_meat()
        range = range or range_model.create_kilogram()
        return nomenclature_model("Курица (тушка)", "Курица тушка охлаждённая", group, range)


    """Фабричный метод - создать номенклатуру "Морковь" """
    @staticmethod
    def create_carrot(group=None, range=None):
        group = group or nomenclature_group_model.create_vegetables()
        range = range or range_model.create_kilogram()
        return nomenclature_model("Морковь", "Морковь свежая мытая", group, range)


    """Фабричный метод - создать номенклатуру "Лук репчатой" """
    @staticmethod
    def create_onion(group=None, range=None):
        group = group or nomenclature_group_model.create_vegetables()
        range = range or range_model.create_kilogram()
        return nomenclature_model("Лук репчатый", "Лук репчатый свежий", group, range)


    """Фабричный метод - создать номенклатуру "Картофель" """
    @staticmethod
    def create_potato(group=None, range=None):
        group = group or nomenclature_group_model.create_vegetables()
        range = range or range_model.create_kilogram()
        return nomenclature_model("Картофель", "Картофель свежий мытый", group, range)


    """Фабричный метод - создать номенклатуру "Лапша домашняя (полуфабрикат)" """
    @staticmethod
    def create_semi_finished_noodles(group=None, range=None):
        group = group or nomenclature_group_model.create_semi_finished()
        range = range or range_model.create_kilogram()
        return nomenclature_model("Лапша домашняя (полуфабрикат)", "Лапша домашняя полуфабрикат замороженный", group, range)


    """Фабричный метод - создать номенклатуру "Сметана 15%" """
    @staticmethod
    def create_sour_cream(group=None, range=None):
        group = group or nomenclature_group_model.create_dairy()
        range = range or range_model.create_kilogram()
        return nomenclature_model("Сметана 15%", "Сметана 15% пастеризованная", group, range)


    """Фабричный метод - создать номенклатуру "Лавровый лист" """
    @staticmethod
    def create_bay_leaf(group=None, range=None):
        group = group or nomenclature_group_model.create_grocery()
        range = range or range_model.create_piece()
        return nomenclature_model("Лавровый лист", "Лавровый лист сухой", group, range)