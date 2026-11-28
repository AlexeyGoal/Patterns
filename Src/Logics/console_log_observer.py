from Src.Core.abstract_observer import abstract_observer
from Src.Dtos.log_event_dto import log_event_dto


"""
Наблюдатель, выводящий события журнала в консоль.
"""
class console_log_observer(abstract_observer):

    """Вывести событие в консоль"""
    def update(self, event: object) -> None:
        if not isinstance(event, log_event_dto):
            raise TypeError("Ожидалось событие log_event_dto")

        print(f"[AUDIT] {event}")


ConsoleLogObserver = console_log_observer
