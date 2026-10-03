from Src.Core.entity import entity
from Src.Core.validator import validator
from Src.Models.organization_model import organization_model


class settings_model(entity):
   
    __organization: organization_model = None
   
    __boss_name: str = ""
    
    __account_name: str = ""

    __is_first_start: bool = False
   
    # карточка организации
    @property
    def organization(self) -> organization_model:
        return self.__organization


    @organization.setter
    def organization(self, value: organization_model) -> None:
        validator.validate(value, organization_model)
        self.__organization = value
    
    # наименование руководителя
    @property
    def boss_name(self) -> str:
        return self.__boss_name

    @boss_name.setter
    def boss_name(self, value: str) -> None:
        validator.validate(value, str, 255)
        self.__boss_name = value.strip()


    # Наименование главного бухгалтера
    @property
    def account_name(self) -> str:
        return self.__account_name

    @account_name.setter
    def account_name(self, value: str) -> None:
        validator.validate(value, str, 255)
        self.__account_name = value.strip()

    
    # Флаг первого старта приложения
    @property
    def is_first_start(self) -> bool:
        return self.__is_first_start

    @is_first_start.setter
    def is_first_start(self, value: bool) -> None:
        validator.validate(value, bool)
        self.__is_first_start = value