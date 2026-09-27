from Src.Core.entity import entity
from Src.Core.exception import arguments_exception

"""Модель организации"""
class organization_model(name_id):
    """ Конструктор организации.""""
    def __init__(self, name="", inn="", bik="", account="", ownership_form=""):
        
        super().__init__()
        self.name = name
        self.inn = inn
        self.bik = bik
        self.account = account
        self.ownership_form = ownership_form

    """Геттер ИНН"""
    @property
    def inn(self):
        
        return self.__inn

    """Сеттер ИНН"""
    @inn.setter
    def inn(self, value):
        
        if not isinstance(value, str):
            raise arguments_exception("inn", "inn must be str")

        value = value.strip()

        if not value.isdigit():
            raise arguments_exception("inn", "inn must contain only digits")

        if len(value) not in (10, 12):
            raise arguments_exception("inn", "inn must contain 10 or 12 digits.")

        self.__inn = value

    """Геттер БИК организации"""
    @property
    def bik(self):
        
        return self.__bik

    """Сеттер БИК организации"""
    @bik.setter
    def bik(self, value):
        
        if not isinstance(value, str):
            raise arguments_exception("bik", "bik must be str")

        value = value.strip()

        if not value.isdigit():
            raise arguments_exception("bik", "bik must contain only digits")

        if len(value) != 9:
            raise arguments_exception("bik", "bik must contain 9 digits")

        self.__bik = value

    """Геттер расчетного счета организации"""
    @property
    def account(self):
        return self.__account
    
    """Cеттер расчетного счета организации"""
    @account.setter
    def account(self, value):
        
        if not isinstance(value, str):
            raise arguments_exception("account", "account must be str")

        value = value.strip()

        if not value.isdigit():
            raise arguments_exception("account", "account must contain only digits")

        if len(value) != 20:
            raise arguments_exception("account", "account must contain 20 digits")

        self.__account = value

    """Геттер формы собственности организации"""
    @property
    def ownership_form(self):
        return self.__ownership_form

    """Сеттер формы собственности организации"""
    @ownership_form.setter
    def ownership_form(self, value):
       
        if not isinstance(value, str):
            raise arguments_exception("ownership_form", "ownership_form must be str")

        value = value.strip()

        if value == "":
            raise arguments_exception("ownership_form", "ownership_form must not be empty")

        if len(value) > 5:
            raise arguments_exception("ownership_form", "ownership_form must not exeed 5")

        self.__ownership_form = value