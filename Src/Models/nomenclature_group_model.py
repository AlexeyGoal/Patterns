from Src.Core.entity import entity
"""Модель группы номенклатуры"""
class nomenclature_group_model(entity):
 
    """Конструктор группы номенклатуры"""
    
    def __init__(self, name=""):
    
        super().__init__()
        self.name = name


    @staticmethod
    def create_grocery():
        """
        Фабричный метод - создать группу "Бакалея".
        """
        return nomenclature_group_model("Бакалея")

    @staticmethod
    def create_dairy():
        """
        Фабричный метод - создать группу "Молочные продукты".
        """
        return nomenclature_group_model("Молочные продукты")

    @staticmethod
    def create_dishes():
        """
        Фабричный метод - создать группу "Блюда".
        """
        return nomenclature_group_model("Блюда")

    """Фабричный метод - создать группу "Упаковка" """
    @staticmethod
    def create_packaging():
        return nomenclature_group_model("Упаковка")


    """Фабричный метод - создать группу "Мясные продукты" """
    @staticmethod
    def create_meat():
        return nomenclature_group_model("Мясные продукты")


    """Фабричный метод - создать группу "Овощи" """
    @staticmethod
    def create_vegetables():
        return nomenclature_group_model("Овощи")


    """Фабричный метод - создать группу "Полуфабрикаты" """
    @staticmethod
    def create_semi_finished():
        return nomenclature_group_model("Полуфабрикаты")


    """Фабричный метод - создать группу "Мясные продукты" """
    @staticmethod
    def create_meat():
        return nomenclature_group_model("Мясные продукты")


    """Фабричный метод - создать группу "Овощи" """
    @staticmethod
    def create_vegetables():
        return nomenclature_group_model("Овощи")


    """Фабричный метод - создать группу "Полуфабрикаты" """
    @staticmethod
    def create_semi_finished():
        return nomenclature_group_model("Полуфабрикаты")