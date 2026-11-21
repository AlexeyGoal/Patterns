from Src.Core.abstract_manager import abstract_manager
from Src.Core.validator import validator, operation_exception
from Src.Logics.deserialize_service import deserialize_service
from Src.Logics.json_deserializer import json_deserializer
from Src.Models.settings_model import settings_model
from Src.Models.organization_model import organization_model
from Src.Models.range_model import range_model


# менеджер настроек
class settings_manager(abstract_manager):
    __default_file_name: str = "settings.json"

    _settings: settings_model = None
    __is_loaded: bool = False
    __data: dict = None


    """Фабричный метод - создать килограмм (делегирует создание range_model)"""
    @staticmethod
    def create_kilogram() -> range_model:
        return range_model.create_kilogram()

    # Singleton
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(settings_manager, cls).__new__(cls)
        return cls.instance

    # Загружает данные настроек из JSON файла через общий механизм десериализации.
    def load(self, file_name: str = "") -> None:
       
        file_name = file_name.strip() or self.__default_file_name
        validator.validate(file_name, str)

        try:
            # Общий механизм десериализации: json_deserializer -> deserialize_service
            self.__data = json_deserializer().load(file_name)
            self.__is_loaded = self.convert()

        except operation_exception:
            raise

        except Exception as ex:
            raise operation_exception(
                f"Ошибка при загрузке данных из файла {file_name}: {ex}"
            ) from ex


    # Преобразует данные JSON в объект settings_model общим механизмом десериализации.
    def convert(self) -> bool:
        
        if isinstance(self.__data, settings_model):
            self._settings = self.__data
            return True

        if not isinstance(self.__data, dict):
            return False

        try:
            prepared = self.__prepare_data(self.__data)
            restored = deserialize_service().deserialize(prepared)

            if not isinstance(restored, settings_model):
                return False

            self._settings = restored
            return True

        except Exception:
            return False


    # Добавляет служебные маркеры $type для файлов настроек без явной типизации.
    @staticmethod
    def __prepare_data(data: dict) -> dict:
        
        prepared = dict(data)
        prepared.setdefault("$type", settings_model.__name__)

        organization = prepared.get("organization")
        if isinstance(organization, dict):
            organization_data = dict(organization)
            organization_data.setdefault("$type", organization_model.__name__)
            prepared["organization"] = organization_data

        return prepared

    # Флаг успешности загрузки настроек
    @property
    def is_loaded(self) -> bool:
        return self.__is_loaded

    # Объект настроек settings_model
    @property
    def settings(self) -> settings_model:
        return self._settings