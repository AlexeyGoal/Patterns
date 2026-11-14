import json
import uuid

import pytest

from Src.Core.entity import entity
from Src.Logics.serialize_factory import serialize_factory, SerializeFactory
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.recipe_item_model import recipe_item_model
from Src.Models.recipe_model import recipe_model


# Фикстура: универсальная фабрика сериализации
@pytest.fixture
def serializer():
    return serialize_factory()


"""Тест: у модели появляется служебный маркер $type"""
def test_entity_has_type_marker(serializer):
    gram = range_model.create_gram()

    result = serializer.convert(gram)

    assert result["$type"] == "range_model"
    assert result["name"] == "грамм"
    assert result["conversion_factor"] == 1
    assert result["base_range"] is None


"""Тест: id выгружается строкой, пригодной для JSON"""
def test_uuid_exported_as_string(serializer):
    gram = range_model.create_gram()

    result = serializer.convert(gram)

    assert isinstance(result["id"], str)
    assert uuid.UUID(result["id"]) == gram.id


"""Тест: вложенные ссылки получают собственный $type"""
def test_nested_references_have_type_marker(serializer):
    flour = nomenclature_model.create_flour()

    result = serializer.convert(flour)

    assert result["$type"] == "nomenclature_model"
    assert result["group"]["$type"] == "nomenclature_group_model"
    assert result["range"]["$type"] == "range_model"
    assert result["range"]["base_range"]["$type"] == "range_model"


"""Тест: поля-коллекции выгружаются рекурсивно"""
def test_collections_are_serialized(serializer):
    gram = range_model.create_gram()
    recipe = recipe_model.create("Тестовый рецепт", "Описание")
    recipe.add_item(recipe_item_model.create_ingredient("Мука", 200, gram))

    result = serializer.convert(recipe)

    assert result["$type"] == "recipe_model"
    assert result["items"][0]["$type"] == "recipe_item_model"
    assert result["items"][0]["range"]["$type"] == "range_model"
    assert result["sub_recipes"] == []


"""Тест: вычисляемые свойства рецепта не попадают в JSON"""
def test_recipe_derived_fields_excluded(serializer):
    recipe = recipe_model.create_first_start_recipe()

    result = serializer.convert(recipe)

    for field in ("ingredients", "semi_finished_products", "net_weight", "gross_weight", "is_composite"):
        assert field not in result


"""Тест: вычисляемые свойства позиции рецепта не попадают в JSON"""
def test_recipe_item_derived_fields_excluded(serializer):
    item = recipe_item_model.create_ingredient("Мука", 200, range_model.create_gram())

    result = serializer.convert(item)

    for field in ("unique_code", "brutto", "netto"):
        assert field not in result


"""Тест: список моделей превращается в список словарей"""
def test_convert_list_of_entities(serializer):
    units = [range_model.create_gram(), range_model.create_kilogram()]

    result = serializer.convert(units)

    assert isinstance(result, list)
    assert [item["$type"] for item in result] == ["range_model", "range_model"]
    assert result[1]["base_range"]["name"] == "грамм"


"""Тест: обычный словарь обходится рекурсивно"""
def test_convert_plain_dict(serializer):
    gram = range_model.create_gram()

    result = serializer.convert({"unit": gram, "count": 2})

    assert result["unit"]["$type"] == "range_model"
    assert result["count"] == 2


"""Тест: простые значения возвращаются как есть"""
@pytest.mark.parametrize("value", [None, True, 42, 3.14, "текст"])
def test_convert_basic_value(serializer, value):
    assert serializer.convert(value) == value


"""Тест: сериализованный рецепт можно записать в JSON без default"""
def test_serialized_data_is_json_ready(serializer):
    recipe = recipe_model.create_first_start_recipe()

    text = json.dumps(serializer.convert(recipe), ensure_ascii=False)

    assert "Суп-лапша домашняя" in text
    assert json.loads(text)["$type"] == "recipe_model"


"""Тест: пользовательская модель сериализуется без отдельного конвертора"""
def test_custom_model_serialized(serializer):
    class custom_entity(entity):
        def __init__(self, name="", comment=""):
            super().__init__()
            self.name = name
            self.comment = comment

    result = serializer.convert(custom_entity("Тест", "Комментарий"))

    assert result["$type"] == "custom_entity"
    assert result["name"] == "Тест"
    assert result["comment"] == "Комментарий"



