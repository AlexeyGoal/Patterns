from Src.Core.entity import entity
from Src.Logics.entity_registry import entity_metadata_registry
from Src.Logics.entity_store import entity_store



class entity_references:

    def __init__(self, registry: entity_metadata_registry, store: entity_store):

        self.__registry = registry
        self.__store = store


    # Найти сущности, которые ссылаются на указанную сущность
    def find_dependents(
        self,
        entity_type: str,
        item: entity,
    ) -> list[tuple[str, entity]]:

        dependents = []
        target_id = str(item.id)

        for candidate_type in self.__registry.types:
            for candidate in self.__store.values(candidate_type):

                if candidate is item:
                    continue

                if self.__has_reference(candidate, target_id, set()):
                    dependents.append((candidate_type, candidate))

        return dependents


    # Человекочитаемое описание зависимостей
    @staticmethod
    def format_dependents(dependents: list[tuple[str, entity]]) -> str:

        return ", ".join(
            f"{entity_type}:{candidate.name} ({candidate.id})"
            for entity_type, candidate in dependents
        )


    # Рекурсивно проверить, содержит ли объект ссылку на сущность с кодом target_id
    def __has_reference(self, value: object, target_id: str, visited: set) -> bool:

        if isinstance(value, entity):

            if str(value.id) == target_id:
                return True

            marker = id(value)

            if marker in visited:
                return False

            visited.add(marker)

            for field in self.__model_fields(value):
                if self.__has_reference(getattr(value, field, None), target_id, visited):
                    return True

            return False

        if isinstance(value, (list, tuple, set)):
            return any(
                self.__has_reference(item, target_id, visited)
                for item in value
            )

        if isinstance(value, dict):
            return any(
                self.__has_reference(item, target_id, visited)
                for item in value.values()
            )

        return False


    # Поля модели, по которым может идти ссылка
    def __model_fields(self, model: entity) -> list[str]:

        metadata = self.__registry.get_by_model(type(model))

        if metadata is not None:
            return list(metadata.relations)

        return [
            name
            for name in dir(model)
            if not name.startswith("_")
            and isinstance(getattr(type(model), name, None), property)
        ]


EntityReferences = entity_references
