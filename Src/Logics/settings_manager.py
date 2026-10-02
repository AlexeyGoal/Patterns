from Src.Core.abstract_manager import abstract_manager
from Src.Core.validator import validator, operation_exception
from Src.Models.settings_model import settings_model
from Src.Models.organization_model import organization_model
import json


class settings_manager(abstract_manager):
    __default_file_name: str = "settings.json"

    _settings: settings_model = None
    __is_loaded: bool = False
    __data: dict = None

    # Singleton
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(settings_manager, cls).__new__(cls)
        return cls.instance

    # Загружает данные настроек из JSON файла.
    def load(self, file_name: str = "") -> None:
       
        file_name = file_name.strip() or self.__default_file_name
        validator.validate(file_name, str)

        try:
            with open(file_name, "r", encoding="utf-8") as file:
                self.__data = json.load(file)

            self.__is_loaded = self.convert()

        except Exception as ex:
            raise operation_exception(
                f"Ошибка при загрузке данных из файла {file_name}: {ex}"
            ) from ex


    # Преобразует сырые данные JSON в объект settings_model.
    def convert(self) -> bool:
        
        if not isinstance(self.__data, dict):
            return False

        try:
            if self._settings is None:
                self._settings = settings_model()

            org = self.__data.get("organization")
            if isinstance(org, dict) and org.get("name") and org.get("inn"):
                self._settings.organization = organization_model(**org)

            for key in ("boss_name", "account_name"):
                value = self.__data.get(key)
                if value and str(value).strip():
                    setattr(self._settings, key, str(value).strip())

            if "is_first_start" in self.__data:
                self._settings.is_first_start = bool(self.__data.get("is_first_start"))

            return True

        except Exception:
            return False

    # Флаг успешности загрузки настроек
    @property
    def is_loaded(self) -> bool:
        return self.__is_loaded

    # Объект настроек settings_model
    @property
    def settings(self) -> settings_model:
        return self._settings