from Src.Core.abstract_convertor import abstract_convertor, AbstractConvertor
from Src.Core.entity import entity
from Src.Core.exception import arguments_exception


"""
Конвертор ссылок
"""
class reference_convertor(abstract_convertor):
    

    """Проверить, что значение относится к типу Reference"""
    @staticmethod
    def is_supported(source: object) -> bool:

        return isinstance(source, entity)


    """
    Возвращает словарь всех публичных полей сущности.
    """
    def convert(self, source: object) -> dict:

        if not self.is_supported(source):
            raise arguments_exception("source", "reference_convertor supports only Reference type (entity child)")

        return self.__expand_entity(source, set())


    """
    Раскрыть сущность в словарь её публичных полей.
    """
    def __expand_entity(self, source: entity, visited: set) -> dict:

        # копия цепочки: ветки обхода не влияют друг на друга
        visited = visited | {id(source)}

        result = {}

        for name in dir(type(source)):

            if name.startswith("_"):
                continue

            # пропускает всё, что не является property
            if not isinstance(getattr(type(source), name, None), property):
                continue

            try:
                value = getattr(source, name)
            except Exception as error:
                raise arguments_exception("source", f"property '{name}' cannot be read: {error}")

            result[name] = self.__expand_value(value, visited)

        return result


    """
    Раскрыть значение поля: сущность - в словарь, списки и словари - обойти, остальное - как есть.
    """
    def __expand_value(self, value: object, visited: set) -> object:

        if isinstance(value, entity):

            # ссылка на сущность из цепочки родителей раскрывается до id, иначе рекурсия бесконечна
            if id(value) in visited:
                return value.id

            return self.__expand_entity(value, visited)

        if isinstance(value, dict):
            return {key: self.__expand_value(item, visited) for key, item in value.items()}

        if isinstance(value, (list, tuple)):
            return [self.__expand_value(item, visited) for item in value]

        return value


ReferenceConvertor = reference_convertor
