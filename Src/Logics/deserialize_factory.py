import importlib
import inspect
import pkgutil
import uuid

import Src.Models
from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.entity import entity
from Src.Core.exception import arguments_exception


"""
фабрика десериализации доменных моделей.

"""
class deserialize_factory(abstract_convertor):

   
    TYPE_FIELD = "$type"

    
    __json_names = {
        "item_type": "type",
    }


    """Конструктор: принимает готовый список моделей или находит их автоматически"""
    def __init__(self, model_types: list[type[entity]] = None):

        types = (
            list(model_types)
            if model_types is not None
            else self.__discover_model_types()
        )

        self.__model_types = sorted(types, key=lambda model_type: model_type.__name__)
        self.__mapping = self.__build_mapping(self.__model_types)


    """Фабрика принимает любой объект"""
    @staticmethod
    def is_supported(source: object) -> bool:
        return True


    """Доступные фабрике типы моделей"""
    @property
    def model_types(self) -> list[type[entity]]:
        return list(self.__model_types)


    """Рекурсивно восстановить модели из JSON-совместимых данных"""
    def convert(self, source: object) -> object:

        if isinstance(source, list):
            return [self.convert(item) for item in source]

        if not isinstance(source, dict):

            if source is None or isinstance(source, (str, int, float, bool)):
                return source

            raise arguments_exception("source", "JSON-compatible data expected")

        marker = source.get(self.TYPE_FIELD)

        if marker is None:
            return {key: self.convert(value) for key, value in source.items()}

        return self.__create_model(self.__resolve_model_type(marker), source)


    """Найти класс модели по значению $type"""
    def __resolve_model_type(self, marker: object) -> type[entity]:

        if not isinstance(marker, str) or marker.strip() == "":
            raise arguments_exception(
                self.TYPE_FIELD, "type marker must be a non-empty string"
            )

        model_type = self.__mapping.get(self.__normalize(marker))

        if model_type is None:
            raise arguments_exception(
                self.TYPE_FIELD, f"unknown model type: {marker}"
            )

        return model_type


    """Создать модель через конструктор и восстановить остальные поля"""
    def __create_model(self, model_type: type[entity], source: dict) -> entity:

        parameters = self.__get_constructor_parameters(model_type)
        arguments = {}

        for parameter_name, parameter in parameters.items():

            json_name = self.__json_names.get(parameter_name, parameter_name)

            if json_name in source:
                arguments[parameter_name] = self.__to_value(source[json_name])

            elif parameter.default is inspect.Parameter.empty:
                raise arguments_exception(
                    parameter_name, "required constructor parameter is missing"
                )

        try:
            model = model_type(**arguments)
        except TypeError as error:
            raise arguments_exception(
                "model", f"cannot create {model_type.__name__}: {error}"
            ) from error

        if "id" in source:
            model.id = self.__to_uuid(source["id"])

        self.__apply_collections(model, source)
        self.__apply_properties(model, source)

        return model


    """Рекурсивно восстановить значение поля из JSON"""
    def __to_value(self, value: object) -> object:

        if isinstance(value, (dict, list)):
            return self.convert(value)

        return value


    """Добавить элементы полей-коллекций через методы модели"""
    def __apply_collections(self, model: entity, source: dict) -> None:

        for field_name, adder_name in self.__get_collection_fields(type(model)).items():

            if field_name not in source:
                continue

            values = source[field_name]

            if not isinstance(values, list):
                continue

            adder = getattr(model, adder_name)

            for value in values:
                restored = self.convert(value)
                if isinstance(restored, entity):
                    adder(restored)


    """Установить свойства модели через публичные сеттеры"""
    def __apply_properties(self, model: entity, source: dict) -> None:

        constructor_fields = set(self.__get_constructor_fields(type(model)))
        collection_fields = set(self.__get_collection_fields(type(model)))

        for property_name in self.__get_writable_properties(type(model)):

            if property_name == "id":
                continue

            if property_name in constructor_fields:
                continue

            if property_name in collection_fields:
                continue

            if property_name not in source:
                continue

            value = self.__to_value(source[property_name])

            if value is None:
                continue

            # Пустая строка означает «поле не заполнено»: значение по умолчанию
            # модели уже хранит это состояние, а сеттеры такие значения отвергают.
            if isinstance(value, str) and value.strip() == "":
                continue

            if self.__already_in_collection(model, value):
                continue

            setattr(model, property_name, value)


    """Проверить, что объект-ссылка уже добавлен в коллекцию модели"""
    @staticmethod
    def __already_in_collection(model: entity, value: object) -> bool:

        if not isinstance(value, entity):
            return False

        items = getattr(model, "items", None)

        if not isinstance(items, list):
            return False

        return any(getattr(item, "id", None) == value.id for item in items)


    """Преобразовать идентификатор из JSON в UUID"""
    @staticmethod
    def __to_uuid(value: object) -> uuid.UUID:

        if isinstance(value, uuid.UUID):
            return value

        try:
            return uuid.UUID(str(value))
        except (ValueError, TypeError, AttributeError) as error:
            raise arguments_exception(
                "id", f"id must be a valid UUID: {error}"
            ) from error


    """Построить соответствие «нормализованное имя типа → модель»"""
    def __build_mapping(self, model_types: list[type[entity]]) -> dict[str, type[entity]]:

        mapping = {}

        for model_type in model_types:

            name = model_type.__name__
            mapping[self.__normalize(name)] = model_type

            if name.lower().endswith("_model"):
                mapping[self.__normalize(name[:-6])] = model_type

        return mapping


    """Нормализовать имя типа: регистр и подчёркивания не важны"""
    @staticmethod
    def __normalize(marker: str) -> str:
        return marker.strip().lower().replace("_", "")


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

            adder = deserialize_factory.__find_adder(name, methods)

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


    """Импортировать и собрать все доменные модели проекта"""
    @staticmethod
    def __discover_model_types() -> list[type[entity]]:

        for module_info in pkgutil.iter_modules(Src.Models.__path__):

            if module_info.name.startswith("_"):
                continue

            importlib.import_module(f"Src.Models.{module_info.name}")

        result = []
        deserialize_factory.__collect_model_types(entity, result)

        return sorted(result, key=lambda model_type: model_type.__name__)


    """Рекурсивно собрать неабстрактные наследники entity из каталога Models"""
    @staticmethod
    def __collect_model_types(
        parent: type[entity],
        result: list[type[entity]],
    ) -> None:

        for model_type in parent.__subclasses__():

            if not model_type.__module__.startswith("Src.Models."):
                continue

            if inspect.isabstract(model_type):
                continue

            if model_type not in result:
                result.append(model_type)

            deserialize_factory.__collect_model_types(model_type, result)


DeserializeFactory = deserialize_factory
