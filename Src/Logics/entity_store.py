from Src.Core.entity import entity
from Src.Core.exception import arguments_exception
from Src.Logics.storage_manager import storage_manager


"""
Доступ к коллекциям доменных сущностей в storage_manager.
"""
class entity_store:

    def __init__(self, manager: storage_manager = None):

        self.__manager = manager if manager is not None else storage_manager()


    # Публичная коллекция сущностей указанного типа
    def collection(self, entity_type: str) -> dict:

        name = self.__collection_name(entity_type)

        if name is None:
            raise arguments_exception(
                "entity_type",
                f"Для типа сущности '{entity_type}' не найдена коллекция",
            )

        return getattr(self.__manager, name)


    # Все сущности указанного типа
    def values(self, entity_type: str) -> list[entity]:

        return list(self.collection(entity_type).values())


    # Найти сущность по типу и коду
    def find(self, entity_type: str, entity_code: str) -> entity | None:

        for item in self.collection(entity_type).values():
            if str(item.id) == str(entity_code):
                return item

        return None


    # Добавить модель в коллекцию storage_manager
    def add(self, entity_type: str, item: entity) -> bool:

        adder = getattr(self.__manager, f"add_{entity_type}", None)

        if not callable(adder):
            raise arguments_exception(
                "entity_type",
                f"Менеджер не поддерживает добавление сущности '{entity_type}'",
            )

        return bool(adder(item))


    # Удалить модель из коллекции storage_manager
    def remove(self, entity_type: str, item: entity) -> None:

        self.collection(entity_type).pop(item.id, None)


    # Имя публичной коллекции менеджера, выведенное из типа сущности
    def __collection_name(self, entity_type: str) -> str | None:

        normalized = (entity_type or "").strip().lower()

        if normalized == "":
            return None

        candidates = [
            f"{normalized}s",
            f"{normalized}es",
            normalized,
        ]

        for candidate in candidates:
            if isinstance(getattr(self.__manager, candidate, None), dict):
                return candidate

        return None


EntityStore = entity_store
