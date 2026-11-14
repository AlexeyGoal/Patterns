import inspect
import uuid

from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.entity import entity


"""
Универсальная фабрика сериализации доменных моделей.
"""
class serialize_factory(abstract_convertor):

    
    TYPE_FIELD = "$type"

    
    __json_names = {
        "item_type": "type",
    }


    """Фабрика принимает любой объект"""
    @staticmethod
    def is_supported(source: object) -> bool:
        return True


    """Превратить модель в JSON-совместимый словарь"""
    def convert(self, source: object) -> object:

        if isinstance(source, (list, tuple)):
            return [self.convert(item) for item in source]

        if isinstance(source, dict):
            return {key: self.convert(value) for key, value in source.items()}

        if isinstance(source, uuid.UUID):
            return str(source)

        if not isinstance(source, entity):
            return source

        result = {self.TYPE_FIELD: type(source).__name__}

        for field in self.__get_fields(source):
            result[field] = self.convert(getattr(source, field))

        return result


    """Поля модели, которые участвуют в сериализации"""
    def __get_fields(self, source: object) -> list[str]:

        model_type = type(source)
        result = []

        for field in self.__get_constructor_fields(model_type):
            if field not in result:
                result.append(field)

        for field in self.__get_writable_properties(model_type):
            if field not in result:
                result.append(field)

        for field in self.__get_collection_fields(model_type):
            if field not in result:
                result.append(field)

        return result


    """Параметры конструктора модели без self и *args/**kwargs"""
    @staticmethod
    def __get_constructor_parameters(model_type: type) -> dict:

        if not inspect.isclass(model_type) or not issubclass(model_type, entity):
            return {}

        signature = inspect.signature(model_type)

        return {
            name: parameter
            for name, parameter in signature.parameters.items()
            if name != "self"
            and parameter.kind not in (
                parameter.VAR_POSITIONAL,
                parameter.VAR_KEYWORD,
            )
        }


    """Соответствие «поле JSON → параметр конструктора»"""
    @classmethod
    def __get_constructor_fields(cls, model_type: type) -> dict[str, str]:

        return {
            cls.__json_names.get(name, name): name
            for name in cls.__get_constructor_parameters(model_type)
        }


    """Публичные свойства модели, у которых есть сеттер"""
    @staticmethod
    def __get_writable_properties(model_type: type) -> dict[str, str]:

        result = {}

        for name in dir(model_type):

            if name.startswith("_"):
                continue

            attribute = getattr(model_type, name, None)

            if isinstance(attribute, property) and attribute.fset is not None:
                result[name] = name

        return result


    """Свойства-коллекции: имя свойства → метод добавления элемента"""
    @staticmethod
    def __get_collection_fields(model_type: type) -> dict[str, str]:

        result = {}
        methods = {name for name in dir(model_type) if name.startswith("add_")}

        for name in dir(model_type):

            if name.startswith("_"):
                continue

            attribute = getattr(model_type, name, None)

            if not isinstance(attribute, property) or attribute.fget is None:
                continue

            adder = serialize_factory.__find_adder(name, methods)

            if adder is not None:
                result[name] = adder

        return result


    """Найти метод add_* для свойства-коллекции"""
    @staticmethod
    def __find_adder(property_name: str, methods: set[str]) -> str | None:

        candidates = [f"add_{property_name}"]

        if property_name.endswith("ies"):
            candidates.append(f"add_{property_name[:-3]}y")

        if property_name.endswith("es"):
            candidates.append(f"add_{property_name[:-2]}")

        if property_name.endswith("s"):
            candidates.append(f"add_{property_name[:-1]}")

        for candidate in candidates:
            if candidate in methods:
                return candidate

        return None


SerializeFactory = serialize_factory
