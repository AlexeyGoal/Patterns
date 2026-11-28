from abc import ABC, abstractmethod


"""
Абстрактный наблюдатель.
"""
class abstract_observer(ABC):

    """Обработать событие, полученное от субъекта"""
    @abstractmethod
    def update(self, event: object) -> None:
        pass


AbstractObserver = abstract_observer
