import datetime
import uuid
from enum import Enum

from Src.Core.log_type import log_category, log_operation, log_status


"""
DTO события журнала аудита.
"""
class log_event_dto:

    """Конструктор события журнала"""
    def __init__(
        self,
        category: object = log_category.CRUD,
        operation: object = log_operation.READ,
        status: object = log_status.SUCCESS,
        entity_type: str = "",
        entity_code: str = "",
        message: str = "",
        details: dict = None,
        source: str = "",
        created_at: datetime.datetime = None,
    ) -> None:

        self.__category = self.__enum_value(category)
        self.__operation = self.__enum_value(operation)
        self.__status = self.__enum_value(status)
        self.__entity_type = str(entity_type or "").strip().lower()
        self.__entity_code = str(entity_code or "").strip()
        self.__message = str(message or "").strip()
        self.__details = self.__json_safe(details if details is not None else {})
        self.__source = str(source or "").strip()
        self.__created_at = created_at if created_at is not None else datetime.datetime.now()


    """Категория события (CRUD, WAREHOUSE, WEB, SETTINGS)"""
    @property
    def category(self) -> str:
        return self.__category


    """Операция события (CREATE, READ, UPDATE, DELETE, ...)"""
    @property
    def operation(self) -> str:
        return self.__operation


    """Результат операции (SUCCESS или FAILURE)"""
    @property
    def status(self) -> str:
        return self.__status


    """Тип доменной сущности, к которой относится событие"""
    @property
    def entity_type(self) -> str:
        return self.__entity_type


    """Код доменной сущности, к которой относится событие"""
    @property
    def entity_code(self) -> str:
        return self.__entity_code


    """Краткое описание события"""
    @property
    def message(self) -> str:
        return self.__message


    """Дополнительные структурированные данные события"""
    @property
    def details(self) -> dict:
        return dict(self.__details)


    """Источник события"""
    @property
    def source(self) -> str:
        return self.__source


    """Дата и время возникновения события"""
    @property
    def created_at(self) -> datetime.datetime:
        return self.__created_at


    """Сериализовать событие в JSON-совместимый словарь"""
    def to_dict(self) -> dict:
        return {
            "timestamp": self.__created_at.isoformat(timespec="seconds"),
            "category": self.__category,
            "operation": self.__operation,
            "status": self.__status,
            "entity_type": self.__entity_type,
            "entity_code": self.__entity_code,
            "message": self.__message,
            "source": self.__source,
            "details": self.__details,
        }


    """Строковое представление события для консольного наблюдателя"""
    def __str__(self) -> str:
        parts = [
            self.__created_at.strftime("%Y-%m-%d %H:%M:%S"),
            self.__category,
            self.__operation,
            self.__status,
        ]

        if self.__entity_type:
            target = self.__entity_type
            if self.__entity_code:
                target = f"{target}:{self.__entity_code}"
            parts.append(target)

        if self.__message:
            parts.append(self.__message)

        return " | ".join(parts)


    """Привести значение перечисления к строке"""
    @staticmethod
    def __enum_value(value: object) -> str:
        if isinstance(value, Enum):
            return str(value.value).strip().upper()

        return str(value or "").strip().upper()


    """Рекурсивно привести данные к JSON-совместимому виду"""
    @classmethod
    def __json_safe(cls, value: object) -> object:

        if value is None or isinstance(value, (str, int, float, bool)):
            return value

        if isinstance(value, uuid.UUID):
            return str(value)

        if isinstance(value, (datetime.datetime, datetime.date, datetime.time)):
            return value.isoformat()

        if isinstance(value, dict):
            return {
                str(key): cls.__json_safe(item)
                for key, item in value.items()
            }

        if isinstance(value, (list, tuple, set)):
            return [cls.__json_safe(item) for item in value]

        return str(value)


LogEventDto = log_event_dto
