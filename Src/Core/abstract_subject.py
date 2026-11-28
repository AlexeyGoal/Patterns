from abc import ABC

from Src.Core.abstract_observer import abstract_observer


"""
Абстрактный субъект (наблюдаемый объект).
"""
class abstract_subject(ABC):

    """Конструктор субъекта"""
    def __init__(self) -> None:
        self.__observers: list[abstract_observer] = []


    """Текущий список подписчиков"""
    @property
    def observers(self) -> tuple[abstract_observer, ...]:
        return tuple(self.__observers)


    """Подписать наблюдателя на события субъекта"""
    def attach(self, observer: abstract_observer) -> None:
        if not isinstance(observer, abstract_observer):
            raise TypeError("Наблюдатель должен наследовать abstract_observer")

        if observer not in self.__observers:
            self.__observers.append(observer)


    """Отписать наблюдателя от событий субъекта"""
    def detach(self, observer: abstract_observer) -> None:
        if observer in self.__observers:
            self.__observers.remove(observer)


    """Отписать всех наблюдателей"""
    def detach_all(self) -> None:
        self.__observers.clear()


    """Разослать событие всем подписчикам"""
    def notify(self, event: object) -> None:
        for observer in list(self.__observers):
            try:
                observer.update(event)
            except Exception:
               
                continue


AbstractSubject = abstract_subject
