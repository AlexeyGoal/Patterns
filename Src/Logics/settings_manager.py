from Src.Core.abstract_manager import abstract_manager
from Src.Core.exception import arguments_exception
from Src.Core.log_type import log_category, log_operation, log_status
from Src.Core.validator import validator, operation_exception
from Src.Dtos.log_event_dto import log_event_dto
from Src.Logics.deserialize_service import deserialize_service
from Src.Logics.json_deserializer import json_deserializer
from Src.Logics.logging_service import logging_service
from Src.Logics.serialize_factory import serialize_factory
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

            self.__log_settings(
                log_operation.LOAD,
                log_status.SUCCESS if self.__is_loaded else log_status.FAILURE,
                message=f"Настройки загружены из файла {file_name}",
                details={"file": file_name, "loaded": self.__is_loaded},
            )

        except operation_exception as ex:
            self.__log_settings(
                log_operation.LOAD,
                log_status.FAILURE,
                message=str(ex),
                details={"file": file_name},
            )
            raise

        except Exception as ex:
            error = operation_exception(
                f"Ошибка при загрузке данных из файла {file_name}: {ex}"
            )
            self.__log_settings(
                log_operation.LOAD,
                log_status.FAILURE,
                message=str(error),
                details={"file": file_name},
            )
            raise error from ex


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


    # Изменить параметры настроек и зафиксировать изменения в журнале
    def update(self, payload: dict) -> settings_model:

        try:
            return self.__apply_update(payload)

        except Exception as ex:
            self.__log_settings(
                log_operation.UPDATE,
                log_status.FAILURE,
                message=f"Ошибка изменения настроек: {ex}",
                details={"payload": payload},
            )
            raise


    # Применить изменения настроек
    def __apply_update(self, payload: dict) -> settings_model:

        if not isinstance(payload, dict):
            raise arguments_exception(
                "payload", "Тело запроса должно быть JSON-объектом"
            )

        if self._settings is None:
            self.load()

        if self._settings is None:
            raise operation_exception("Настройки не загружены")

        before = self.to_dict()

        writable = self.__writable_parameters()
        data = dict(before)

        for field, value in payload.items():

            if field not in writable:
                raise arguments_exception(
                    field, f"Неизвестный параметр настроек: '{field}'"
                )

            if isinstance(value, str) and value.strip() == "":
                raise arguments_exception(
                    field, f"Параметр '{field}' должен быть непустой строкой"
                )

            if field == "organization":
                data["organization"] = self.__merge_organization(
                    data.get("organization"),
                    value,
                )
            else:
                data[field] = value

        
        prepared = self.__prepare_data(data)
        restored = deserialize_service().deserialize(prepared)

        if not isinstance(restored, settings_model):
            raise operation_exception("Не удалось изменить параметры настроек")

        after = serialize_factory().convert(restored)

        self._settings = restored
        self.__is_loaded = True

        self.__log_settings(
            log_operation.UPDATE,
            log_status.SUCCESS,
            message="Изменены параметры настроек",
            details={"before": before, "after": after},
        )

        return self._settings


    # Параметры настроек, доступные для изменения (свойства модели с сеттером)
    def __writable_parameters(self) -> set[str]:

        return {
            name
            for name, value in vars(type(self._settings)).items()
            if isinstance(value, property) and value.fset is not None
        }


    # Сериализовать настройки в JSON-совместимый словарь
    def to_dict(self) -> dict:

        if self._settings is None:
            return {}

        return serialize_factory().convert(self._settings)


    # Наложить изменения на карточку организации
    @staticmethod
    def __merge_organization(current: object, value: object) -> dict:

        if isinstance(value, organization_model):
            return serialize_factory().convert(value)

        if not isinstance(value, dict):
            raise arguments_exception(
                "organization", "Параметр organization должен быть JSON-объектом"
            )

        data = dict(current) if isinstance(current, dict) else {}
        data.update(value)
        data["$type"] = organization_model.__name__

        return data


    # Записать событие изменения настроек в журнал
    @staticmethod
    def __log_settings(
        operation: object,
        status: object,
        message: str = "",
        details: dict = None,
    ) -> None:

        try:
            event = log_event_dto(
                category=log_category.SETTINGS,
                operation=operation,
                status=status,
                entity_type="settings",
                message=message,
                details=details,
                source="settings_manager",
            )
            logging_service().log(event)
        except Exception:
            # Сбой журналирования не должен прерывать изменение настроек.
            pass
