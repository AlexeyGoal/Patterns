import json
import os
import threading

from Src.Core.abstract_observer import abstract_observer
from Src.Dtos.log_event_dto import log_event_dto


"""
Наблюдатель, записывающий события журнала в JSON-файл.
"""
class file_log_observer(abstract_observer):

    """Конструктор наблюдателя"""
    def __init__(self, file_name: str = "logs/audit.json") -> None:
        self.__file_name = str(file_name or "logs/audit.json").strip()
        self.__lock = threading.Lock()


    """Путь к файлу журнала"""
    @property
    def file_name(self) -> str:
        return self.__file_name


    """Добавить событие в JSON-массив файла"""
    def update(self, event: object) -> None:
        if not isinstance(event, log_event_dto):
            raise TypeError("Ожидалось событие log_event_dto")

        directory = os.path.dirname(self.__file_name)
        if directory:
            os.makedirs(directory, exist_ok=True)

        with self.__lock:
            events = self.__read_events()
            events.append(event.to_dict())

            temporary = f"{self.__file_name}.tmp"
            with open(temporary, "w", encoding="utf-8") as stream:
                json.dump(events, stream, ensure_ascii=False, indent=2)
                stream.write("\n")

            os.replace(temporary, self.__file_name)


    """Прочитать уже сохраненные события"""
    def __read_events(self) -> list[dict]:

        if not os.path.exists(self.__file_name):
            return []

        try:
            with open(self.__file_name, "r", encoding="utf-8") as stream:
                data = json.load(stream)
        except (json.JSONDecodeError, OSError):
            return []

        if isinstance(data, list):
            return data

        if isinstance(data, dict):
            return [data]

        return []


FileLogObserver = file_log_observer
