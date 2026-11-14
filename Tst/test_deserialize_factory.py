import json
import uuid

import pytest

from Src.Core.entity import entity
from Src.Core.exception import arguments_exception
from Src.Logics.deserialize_factory import deserialize_factory, DeserializeFactory
from Src.Logics.serialize_factory import serialize_factory
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.organization_model import organization_model
from Src.Models.range_model import range_model
from Src.Models.recipe_item_model import recipe_item_model, recipe_item_type
from Src.Models.recipe_model import recipe_model
from Src.Models.settings_model import settings_model
from Src.Models.storage_model import storage_model


# Фикстура: универсальная фабрика десериализации
@pytest.fixture
def factory():
    return deserialize_factory()


# Фикстура: универсальная фабрика сериализации
@pytest.fixture
def serializer():
    return serialize_factory()


# Прогнать данные через текст JSON, как при реальной загрузке из файла
def as_json(data):
    return json.loads(json.dumps(data, ensure_ascii=False, default=str))


# Тестовая модель, которой нет в каталоге Models
class test_custom_entity(entity):

    def __init__(self, name="", comment=""):
        super().__init__()
        self.name = name
        self.comment = comment


"""Тест: простые значения JSON возвращаются без изменений"""
@pytest.mark.parametrize("value", [None, True, False, 42, 3.14, "текст"])
def test_convert_basic_value(factory, value):
    assert factory.convert(value) == value


"""Тест: список обходится рекурсивно"""
def test_convert_list_recursively(factory):
    data = [
        {"$type": "range", "name": "грамм", "conversion_factor": 1, "base_range": None},
        {"$type": "range", "name": "килограмм", "conversion_factor": 1000, "base_range": None},
    ]

    result = factory.convert(data)

    assert len(result) == 2
    assert all(isinstance(item, range_model) for item in result)
    assert result[0].name == "грамм"


"""Тест: обычный словарь без модели обходится рекурсивно"""
def test_convert_plain_dict_recursively(factory):
    data = {"items": [1, 2], "meta": {"count": 2}}

    assert factory.convert(data) == data


"""Тест: модель выбирается по явному маркеру $type"""
def test_convert_by_dollar_type(factory):
    data = {
        "$type": "range",
        "id": "0fd16cdf-c5db-4a3d-8b09-d96bca173ebe",
        "name": "грамм",
        "conversion_factor": 1,
        "base_range": None,
    }

    result = factory.convert(data)

    assert isinstance(result, range_model)
    assert str(result.id) == data["id"]
    assert result.name == "грамм"
    assert result.conversion_factor == 1


"""Тест: $type принимает полное имя класса"""
def test_convert_by_full_class_name(factory):
    data = {
        "$type": "nomenclature_model",
        "name": "Мука пшеничная",
        "full_name": "Мука пшеничная высший сорт",
        "group": {"$type": "nomenclature_group", "name": "Бакалея"},
        "range": {
            "$type": "range_model",
            "name": "килограмм",
            "conversion_factor": 1000,
            "base_range": {
                "$type": "range_model",
                "name": "грамм",
                "conversion_factor": 1,
                "base_range": None,
            },
        },
    }

    result = factory.convert(data)

    assert isinstance(result, nomenclature_model)
    assert result.group.name == "Бакалея"
    assert result.range.name == "килограмм"
    assert result.range.base_range.name == "грамм"


"""Тест: единица измерения восстанавливается вместе с базовой единицей"""
def test_convert_range_with_base_range(factory):
    data = {
        "$type": "range_model",
        "id": "0fd16cdf-c5db-4a3d-8b09-d96bca173ebe",
        "name": "килограмм",
        "conversion_factor": 1000,
        "base_range": {
            "$type": "range_model",
            "id": "f9bc2309-f8c2-43d4-928d-052977cd0801",
            "name": "грамм",
            "conversion_factor": 1,
            "base_range": None,
        },
    }

    result = factory.convert(data)

    assert isinstance(result, range_model)
    assert str(result.id) == data["id"]
    assert result.name == "килограмм"
    assert isinstance(result.base_range, range_model)
    assert result.base_range.name == "грамм"
    assert result.base_range.base_range is None


"""Тест: позиция рецепта восстанавливается с вложенными позициями"""
def test_convert_recipe_item_recursively(factory):
    data = {
        "$type": "recipe_item_model",
        "name": "Лапша домашняя (полуфабрикат)",
        "weight": 0.0,
        "type": recipe_item_type.SEMI_FINISHED,
        "range": {"$type": "range", "name": "грамм", "conversion_factor": 1, "base_range": None},
        "items": [
            {
                "$type": "recipe_item_model",
                "name": "Мука пшеничная",
                "weight": 200,
                "type": recipe_item_type.INGREDIENT,
                "range": {"$type": "range", "name": "грамм", "conversion_factor": 1, "base_range": None},
                "items": [],
            }
        ],
    }

    result = factory.convert(data)

    assert isinstance(result, recipe_item_model)
    assert result.type == recipe_item_type.SEMI_FINISHED
    assert len(result.items) == 1
    assert result.items[0].name == "Мука пшеничная"
    assert result.items[0].weight == 200.0


"""Тест: рецепт восстанавливается с позициями, упаковкой и вложенными рецептами"""
def test_convert_recipe_with_collections(factory):
    data = {
        "$type": "recipe_model",
        "name": "Суп-лапша домашняя",
        "description": "Традиционный суп",
        "items": [
            {
                "$type": "recipe_item_model",
                "name": "Курица (тушка)",
                "weight": 900,
                "type": recipe_item_type.INGREDIENT,
                "range": {"$type": "range", "name": "грамм", "conversion_factor": 1, "base_range": None},
                "items": [],
            },
            {
                "$type": "recipe_item_model",
                "name": "Порционная тарелка",
                "weight": 400,
                "type": recipe_item_type.PACKAGING,
                "range": {"$type": "range", "name": "грамм", "conversion_factor": 1, "base_range": None},
                "items": [],
            },
        ],
        "sub_recipes": [
            {
                "$type": "recipe_model",
                "name": "Бульон куриный",
                "description": "Основа супа",
                "items": [],
                "sub_recipes": [],
                "packaging": None,
            }
        ],
        "packaging": {
            "$type": "recipe_item_model",
            "name": "Порционная тарелка",
            "weight": 400,
            "type": recipe_item_type.PACKAGING,
            "range": {"$type": "range", "name": "грамм", "conversion_factor": 1, "base_range": None},
            "items": [],
        },
    }

    result = factory.convert(data)

    assert isinstance(result, recipe_model)
    assert len(result.items) == 2
    assert len(result.sub_recipes) == 1
    assert result.sub_recipes[0].name == "Бульон куриный"
    assert result.is_composite is True
    assert result.packaging is not None
    assert result.packaging.name == "Порционная тарелка"
    assert len(result.items) == 2


"""Тест: настройки восстанавливаются через публичные сеттеры"""
def test_convert_settings_properties(factory):
    data = {
        "$type": "settings_model",
        "id": "0fd16cdf-c5db-4a3d-8b09-d96bca173ebe",
        "name": "",
        "organization": {
            "$type": "organization_model",
            "name": "Ромашка",
            "inn": "4444444444",
            "bik": "012345678",
            "account": "12345678901234567890",
            "ownership_form": "ООО",
        },
        "boss_name": "Иванов Иван Иванович",
        "account_name": "Петрова Анна Сергеевна",
        "is_first_start": True,
        "response_format": "TXT",
    }

    result = factory.convert(data)

    assert isinstance(result, settings_model)
    assert isinstance(result.organization, organization_model)
    assert result.organization.name == "Ромашка"
    assert result.boss_name == "Иванов Иван Иванович"
    assert result.account_name == "Петрова Анна Сергеевна"
    assert result.is_first_start is True
    assert result.response_format == "TXT"


"""Тест: склад и группа номенклатуры восстанавливаются по маркеру типа"""
def test_convert_storage_and_group(factory):
    storage = factory.convert({
        "$type": "storage_model",
        "name": "Основной склад",
        "address": "ул. Промышленная, 5",
    })
    group = factory.convert({"$type": "nomenclature_group_model", "name": "Бакалея"})

    assert isinstance(storage, storage_model)
    assert storage.address == "ул. Промышленная, 5"
    assert isinstance(group, nomenclature_group_model)
    assert group.name == "Бакалея"


"""Тест: id восстанавливается как UUID"""
def test_convert_restores_uuid(factory):
    identifier = uuid.uuid4()
    data = {
        "$type": "range_model",
        "id": str(identifier),
        "name": "грамм",
        "conversion_factor": 1,
        "base_range": None,
    }

    result = factory.convert(data)

    assert isinstance(result.id, uuid.UUID)
    assert result.id == identifier


"""Тест: некорректный id приводит к arguments_exception"""
def test_convert_invalid_id_raises_exception(factory):
    data = {
        "$type": "range_model",
        "id": "not-a-uuid",
        "name": "грамм",
        "conversion_factor": 1,
        "base_range": None,
    }

    with pytest.raises(arguments_exception):
        factory.convert(data)


"""Тест: неизвестный $type приводит к arguments_exception"""
def test_convert_unknown_type_raises_exception(factory):
    with pytest.raises(arguments_exception):
        factory.convert({"$type": "unknown_model", "name": "Тест"})


"""Тест: новую модель можно добавить в фабрику без отдельного десериализатора"""
def test_factory_supports_custom_model_without_new_deserializer():
    factory = deserialize_factory(model_types=[test_custom_entity])

    result = factory.convert({
        "$type": "test_custom_entity",
        "name": "Тест",
        "comment": "Комментарий",
    })

    assert isinstance(result, test_custom_entity)
    assert result.name == "Тест"
    assert result.comment == "Комментарий"


"""Тест: фабрика обнаруживает все модели проекта"""
def test_factory_discovers_all_models(factory):
    names = {model_type.__name__ for model_type in factory.model_types}

    assert {
        "nomenclature_group_model",
        "nomenclature_model",
        "organization_model",
        "range_model",
        "recipe_item_model",
        "recipe_model",
        "settings_model",
        "storage_model",
    }.issubset(names)


"""Тест: пустые необязательные строки настроек не мешают восстановлению"""
def test_convert_settings_with_empty_strings(serializer, factory):
    settings = settings_model()

    data = as_json(serializer.convert(settings))
    result = factory.convert(data)

    assert isinstance(result, settings_model)
    assert result.id == settings.id
    assert result.boss_name == ""
    assert result.account_name == ""
    assert result.is_first_start is False
    assert result.response_format == "TXT"
    assert result.organization is None


"""Тест: сериализованные модели восстанавливаются без потери полей"""
def test_roundtrip_serialized_model(serializer, factory):
    recipe = recipe_model.create_first_start_recipe()

    data = as_json(serializer.convert(recipe))
    result = factory.convert(data)

    assert isinstance(result, recipe_model)
    assert result.id == recipe.id
    assert result.name == recipe.name
    assert result.description == recipe.description
    assert len(result.items) == len(recipe.items)
    assert result.net_weight == pytest.approx(recipe.net_weight)
    assert result.gross_weight == pytest.approx(recipe.gross_weight)


"""Тест: алиас DeserializeFactory указывает на тот же класс"""
def test_alias():
    assert DeserializeFactory is deserialize_factory
