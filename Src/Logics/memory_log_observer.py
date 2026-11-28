from Src.Core.abstract_observer import abstract_observer
from Src.Dtos.log_event_dto import log_event_dto


"""
Наблюдатель, сохраняющий события журнала в памяти.

Используется для быстрого доступа к последним событиям через API
и для проверки логирования в тестах.
"""
class memory_log_observer(abstract_observer):

    """Конструктор наблюдателя"""
    def __init__(self, capacity: int = 1000) -> None:
        self.__capacity = max(int(capacity), 1)
        self.__events: list[log_event_dto] = []


    """Максимальное количество хранимых событий"""
    @property
    def capacity(self) -> int:
        return self.__capacity


    """Сохраненные события (копия списка)"""
    @property
    def events(self) -> list[log_event_dto]:
        return list(self.__events)


    """Добавить событие в память"""
    def update(self, event: object) -> None:
        if not isinstance(event, log_event_dto):
            raise TypeError("Ожидалось событие log_event_dto")

        self.__events.append(event)

        if len(self.__events) > self.__capacity:
            self.__events = self.__events[-self.__capacity:]


    """Очистить журнал в памяти"""
    def clear(self) -> None:
        self.__events.clear()


    """Вернуть события в JSON-совместимом виде"""
    def to_dicts(
        self,
        category: str = None,
        status: str = None,
        limit: int = None,
    ) -> list[dict]:

        events = list(self.__events)
        normalized_category = str(category or "").strip().upper()
        normalized_status = str(status or "").strip().upper()

        if normalized_category:
            events = [
                event for event in events
                if event.category == normalized_category
            ]

        if normalized_status:
            events = [
                event for event in events
                if event.status == normalized_status
            ]

        if limit is not None and limit >= 0:
            events = events[-limit:] if limit > 0 else []

        return [event.to_dict() for event in events]


MemoryLogObserver = memory_log_observer
