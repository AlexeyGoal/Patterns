import datetime
import types
import uuid

import pytest

from Src.Core.entity import entity
from Src.Logics.convert_factory import convert_factory, ConvertFactory
from Src.Logics.reference_convertor import reference_convertor
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.recipe_item_model import recipe_item_model
from Src.Models.recipe_model import recipe_model


# Тестовая сущность с полем даты/времени
class event_entity(entity):

    def __init__(self, title: str, moment: datetime.datetime):
        super().__init__()
        self.name = title
        self.__title = title
        self.__moment = moment

    @property
    def title(self):
        return self.__title

    @property
    def moment(self):
        return self.__moment


# Фикстура: фабрика конвертеров
@pytest.fixture
def factory():
    return convert_factory()


# Фикстура: рецепт с позициями и вложенным полуфабрикатом
@pytest.fixture
def sample_recipe():
    gram = range_model("грамм", 1)
    recipe = recipe_model.create("Тестовый рецепт", "Описание")
    recipe.add_item(recipe_item_model.create_ingredient("Мука", 200, gram))
    recipe.add_item(recipe_item_model.create_ingredient("Вода", 100, gram))

    noodles = recipe_item_model.create_semi_finished("Лапша", 0, gram)
    noodles.add_item(recipe_item_model.create_ingredient("Соль", 5, gram))
    recipe.add_item(noodles)

    return recipe


# Вспомогательная функция: содержит ли значение объекты-сущности
def contains_entity(value) -> bool:
    if isinstance(value, entity):
        return True
    if isinstance(value, dict):
        return any(contains_entity(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return any(contains_entity(item) for item in value)
    return False




"""Тест: простое значение превращается в словарь «тип → значение»"""
@pytest.mark.parametrize("value,expected", [
    ("текст", {"str": "текст"}),
    (42, {"int": 42}),
    (3.14, {"float": 3.14}),
])
def test_convert_basic_value(factory, value, expected):
    assert factory.convert(value) == expected


"""Тест: дата/время превращается в словарь через datetime_convertor"""
def test_convert_datetime(factory):
    moment = datetime.datetime(2026, 10, 24, 12, 30)

    assert factory.convert(moment) == {"datetime": moment}




"""Тест: список справочников превращается в список их словарей"""
def test_convert_list_of_references_returns_dicts(factory):
    result = factory.convert([
        range_model.create_gram("грамм"),
        range_model.create_piece("штука"),
    ])

    assert isinstance(result, list)
    assert len(result) == 2
    assert all(isinstance(item, dict) for item in result)
    assert result[0]["name"] == "грамм"
    assert result[1]["name"] == "штука"




"""Тест: вложенные ссылки попадают в словарь в виде id"""
def test_convert_reference_nested_references_as_ids(factory):
    flour = nomenclature_model.create_flour()

    result = factory.convert(flour)

    assert result["group"] == flour.group.id
    assert result["range"] == flour.range.id
    assert result["full_name"] == "Мука пшеничная высший сорт"


"""Тест: поле даты/времени внутри справочника сохраняется как есть"""
def test_convert_reference_datetime_field(factory):
    moment = datetime.datetime(2026, 10, 24, 12, 30)
    event = event_entity("Отгрузка", moment)

    result = factory.convert(event)

    assert result["moment"] == moment
    assert result["title"] == "Отгрузка"




"""Тест: типы вне поддержки конвертеров дают пустой словарь без исключений"""
@pytest.mark.parametrize("value", [None, True, {"a": 1}, uuid.uuid4(), object()])
def test_convert_unsupported_types_return_empty_dict(factory, value):
    assert factory.convert(value) == {}


"""Тест: фабрика принимает любой объект любого типа без исключений"""
@pytest.mark.parametrize("value", [
    None, True, 42, 3.14, "текст", [1, 2], {"a": 1}, uuid.uuid4(), object(),
    datetime.datetime(2026, 10, 24, 12, 30),
    range_model.create_gram(),
])
def test_convert_accepts_any_object(factory, value):
    result = factory.convert(value)

    assert isinstance(result, (dict, list))



"""Тест: алиас ConvertFactory указывает на тот же класс"""
def test_alias():
    assert ConvertFactory is convert_factory
