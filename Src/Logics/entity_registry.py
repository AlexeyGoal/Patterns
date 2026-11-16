import inspect
import types
import typing
from dataclasses import dataclass

from Src.Core.entity import entity


"""
Описание связи доменной модели с другой моделью.
"""
@dataclass(frozen=True)
class entity_relation:

    # Класс связанной модели
    target: type[entity]

    # Признак коллекции (список) связей
    is_list: bool

    # Признак встроенной модели, которая не хранится отдельной коллекцией
    embedded: bool


"""
Метаданные доменной модели: тип API и связи.
"""
@dataclass(frozen=True)
class entity_metadata:

    # Тип сущности в API (None для встроенных и служебных моделей)
    api_type: str | None

    # Класс доменной модели
    model: type[entity]

    # Связи модели: имя поля -> описание связи
    relations: dict[str, entity_relation]


"""
Реестр метаданных
"""
class entity_metadata_registry:

    def __init__(self, model_types: list[type[entity]] = None):

        models = list(model_types or self.__discover_model_types())
        self.__top_level = self.__discover_entities(models)
        self.__all = {
            model: entity_metadata(
                api_type=self.__api_type(model),
                model=model,
                relations=self.__discover_relations(model, self.__top_level),
            )
            for model in models
        }
        self.__by_api = {
            metadata.api_type: metadata
            for metadata in self.__all.values()
            if metadata.api_type is not None
        }
        self.__aliases = {
            model: self.__discover_aliases(model, self.__all[model].relations)
            for model in models
        }


    # Типы самостоятельных сущностей API
    @property
    def types(self) -> list[str]:
        return list(self.__by_api)


    # Соответствие «тип API -> класс модели»
    @property
    def models(self) -> dict[str, type[entity]]:
        return {
            api_type: metadata.model
            for api_type, metadata in self.__by_api.items()
        }


    # Метаданные по типу API
    def get(self, api_type: str) -> entity_metadata | None:

        return self.__by_api.get(self.__normalize(api_type))


    # Метаданные по классу модели
    def get_by_model(self, model_type: type[entity]) -> entity_metadata | None:

        return self.__all.get(model_type)


    # Тип API для класса модели
    def api_type(self, model_type: type[entity]) -> str | None:

        metadata = self.get_by_model(model_type)
        return metadata.api_type if metadata is not None else None


    # Псевдонимы полей JSON по классу модели
    def aliases_by_model(self, model_type: type[entity]) -> dict[str, str]:

        return dict(self.__aliases.get(model_type, {}))


    # Поддерживается ли тип API
    def supports(self, api_type: str) -> bool:

        return self.get(api_type) is not None


    # Автоматически найти все модели проекта
    @staticmethod
    def __discover_model_types() -> list[type[entity]]:

        from Src.Logics.deserialize_factory import deserialize_factory

        return deserialize_factory().model_types


    # Самостоятельные сущности: модели с явно заданным ENTITY_TYPE
    @classmethod
    def __discover_entities(
        cls,
        models: list[type[entity]],
    ) -> dict[str, type[entity]]:

        result = {}

        for model in models:
            api_type = cls.__api_type(model)

            if api_type is None:
                continue

            if api_type in result and result[api_type] is not model:
                raise ValueError(
                    f"Тип сущности '{api_type}' назначен нескольким моделям: "
                    f"{result[api_type].__name__}, {model.__name__}"
                )

            result[api_type] = model

        return result


    # Собрать связи модели по аннотациям свойств и методов добавления
    @classmethod
    def __discover_relations(
        cls,
        model_type: type[entity],
        top_level: dict[str, type[entity]],
    ) -> dict[str, entity_relation]:

        result = {}
        top_level_models = set(top_level.values())

        for field in dir(model_type):

            if field.startswith("_"):
                continue

            attribute = getattr(model_type, field, None)

            if not isinstance(attribute, property):
                continue

            # Связь описывается либо сеттером, либо методом add_*
            if attribute.fset is None and cls.__find_mutator(model_type, field) is None:
                continue

            target, is_list = cls.__relation_type(model_type, field, attribute)

            if target is None:
                continue

            result[field] = entity_relation(
                target=target,
                is_list=is_list,
                embedded=target not in top_level_models,
            )

        return result


    # Определить тип связи по аннотациям свойства или метода добавления
    @classmethod
    def __relation_type(
        cls,
        model_type: type[entity],
        field: str,
        attribute: property,
    ) -> tuple[type[entity] | None, bool]:

        annotation = None

        if attribute.fset is not None:
            annotation = cls.__hint(attribute.fset, "value")

        if annotation is None and attribute.fget is not None:
            annotation = cls.__hint(attribute.fget, "return")

        target, is_list = cls.__normalize_annotation(annotation)

        if target is not None:
            return target, is_list

        adder_name = cls.__find_mutator(model_type, field)

        if adder_name is None:
            return None, False

        for name, hint in typing.get_type_hints(getattr(model_type, adder_name)).items():

            if name == "return":
                continue

            target, _ = cls.__normalize_annotation(hint)

            if target is not None:
                return target, True

        return None, False


    # Аннотация метода по имени параметра или return
    @staticmethod
    def __hint(method: object, name: str) -> object | None:

        try:
            return typing.get_type_hints(method).get(name)
        except (NameError, TypeError):
            return None


    # Привести аннотацию к классу сущности и признаку списка
    @classmethod
    def __normalize_annotation(
        cls,
        annotation: object,
    ) -> tuple[type[entity] | None, bool]:

        if annotation is None or annotation is inspect.Signature.empty:
            return None, False

        annotation = cls.__unwrap_optional(annotation)
        origin = typing.get_origin(annotation)

        if origin in (list, tuple, set):

            arguments = typing.get_args(annotation)

            if not arguments:
                return None, True

            item_type = cls.__unwrap_optional(arguments[0])

            if cls.__is_entity_type(item_type):
                return item_type, True

            return None, True

        if cls.__is_entity_type(annotation):
            return annotation, False

        return None, False


    # Убрать Optional/None из аннотации
    @classmethod
    def __unwrap_optional(cls, annotation: object) -> object:

        union_types = (typing.Union,)

        if hasattr(types, "UnionType"):
            union_types = union_types + (types.UnionType,)

        if typing.get_origin(annotation) not in union_types:
            return annotation

        arguments = [
            argument
            for argument in typing.get_args(annotation)
            if argument is not type(None)
        ]

        return arguments[0] if len(arguments) == 1 else annotation


    # Является ли значение классом доменной модели
    @staticmethod
    def __is_entity_type(value: object) -> bool:

        return (
            isinstance(value, type)
            and issubclass(value, entity)
            and value is not entity
        )


    # Найти метод add_* для свойства-коллекции
    @classmethod
    def __find_mutator(cls, model_type: type[entity], property_name: str) -> str | None:

        methods = {
            name
            for name in dir(model_type)
            if name.startswith("add_")
        }

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


    # Собрать псевдонимы полей: объявленные моделью и выведенные из связей
    @classmethod
    def __discover_aliases(
        cls,
        model_type: type[entity],
        relations: dict[str, entity_relation],
    ) -> dict[str, str]:

        aliases = {}

        for base in reversed(model_type.__mro__):

            declared = base.__dict__.get("FIELD_ALIASES")

            if not isinstance(declared, dict):
                continue

            for alias, target in declared.items():

                if isinstance(alias, str) and isinstance(target, str):
                    aliases[alias.strip()] = target.strip()

        for field, relation in relations.items():

            if relation.is_list:
                singular = cls.__singular(field)
                aliases.setdefault(f"{singular}_ids", field)

                api_type = cls.__api_type(relation.target)

                if api_type is not None:
                    aliases.setdefault(f"{api_type}_ids", field)
            else:
                aliases.setdefault(f"{field}_id", field)

        return aliases


    # Единственное число имени поля-коллекции
    @staticmethod
    def __singular(field: str) -> str:

        if field.endswith("ies"):
            return f"{field[:-3]}y"

        if field.endswith("s"):
            return field[:-1]

        return field


    # Тип API, объявленный самой моделью
    @staticmethod
    def __api_type(model_type: type[entity]) -> str | None:

        value = model_type.__dict__.get("ENTITY_TYPE")

        if not isinstance(value, str) or value.strip() == "":
            return None

        return value.strip().lower()


    # Нормализация строки типа API
    @staticmethod
    def __normalize(api_type: str) -> str:

        return (api_type or "").strip().lower()


EntityMetadataRegistry = entity_metadata_registry
