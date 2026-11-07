import pytest

from Src.Logics.deserialize_factory import deserialize_factory, DeserializeFactory
from Src.Logics.nomenclature_deserializer import nomenclature_deserializer
from Src.Logics.nomenclature_group_deserializer import nomenclature_group_deserializer
from Src.Logics.organization_deserializer import organization_deserializer
from Src.Logics.range_deserializer import range_deserializer
from Src.Logics.recipe_deserializer import recipe_deserializer
from Src.Logics.recipe_item_deserializer import recipe_item_deserializer
from Src.Logics.settings_deserializer import settings_deserializer
from Src.Logics.storage_deserializer import storage_deserializer


# Фикстура: фабрика десериализаторов
@pytest.fixture
def factory():
    return deserialize_factory()


"""Тест: для группы номенклатуры фабрика выбирает её десериализатор"""
def test_resolve_group_returns_group_deserializer(factory):
    resolved = factory.resolve({"id": "1", "name": "Бакалея"})

    assert [type(deserializer) for deserializer in resolved] == [nomenclature_group_deserializer]


"""Тест: для единицы измерения фабрика выбирает её десериализатор"""
def test_resolve_range_returns_range_deserializer(factory):
    resolved = factory.resolve({
        "id": "1",
        "name": "килограмм",
        "conversion_factor": 1000,
        "base_range": None,
    })

    assert [type(deserializer) for deserializer in resolved] == [range_deserializer]


"""Тест: для склада фабрика выбирает его десериализатор"""
def test_resolve_storage_returns_storage_deserializer(factory):
    resolved = factory.resolve({
        "id": "1",
        "name": "Основной склад",
        "address": "ул. Промышленная, 5",
    })

    assert [type(deserializer) for deserializer in resolved] == [storage_deserializer]


"""Тест: для номенклатуры фабрика выбирает её десериализатор"""
def test_resolve_nomenclature_returns_nomenclature_deserializer(factory):
    resolved = factory.resolve({
        "id": "1",
        "name": "Мука пшеничная",
        "full_name": "Мука пшеничная высший сорт",
        "group": {"id": "2", "name": "Бакалея"},
        "range": {"id": "3", "name": "килограмм", "conversion_factor": 1000, "base_range": None},
    })

    assert [type(deserializer) for deserializer in resolved] == [nomenclature_deserializer]


"""Тест: для позиции рецепта фабрика выбирает её десериализатор"""
def test_resolve_recipe_item_returns_recipe_item_deserializer(factory):
    resolved = factory.resolve({
        "id": "1",
        "name": "Мука",
        "weight": 200.0,
        "type": "ingredient",
        "range": {"id": "2", "name": "грамм", "conversion_factor": 1, "base_range": None},
        "items": [],
    })

    assert [type(deserializer) for deserializer in resolved] == [recipe_item_deserializer]


"""Тест: для рецепта фабрика выбирает его десериализатор"""
def test_resolve_recipe_returns_recipe_deserializer(factory):
    resolved = factory.resolve({
        "id": "1",
        "name": "Суп-лапша домашняя",
        "description": "Традиционный суп",
        "items": [],
        "sub_recipes": [],
    })

    assert [type(deserializer) for deserializer in resolved] == [recipe_deserializer]


"""Тест: для организации фабрика выбирает её десериализатор"""
def test_resolve_organization_returns_organization_deserializer(factory):
    resolved = factory.resolve({
        "id": "1",
        "name": "Ромашка",
        "inn": "4444444444",
        "bik": "012345678",
        "account": "12345678901234567890",
        "ownership_form": "ООО",
    })

    assert [type(deserializer) for deserializer in resolved] == [organization_deserializer]


"""Тест: для настроек приложения фабрика выбирает их десериализатор"""
def test_resolve_settings_returns_settings_deserializer(factory):
    resolved = factory.resolve({
        "id": "1",
        "name": "",
        "is_first_start": True,
        "response_format": "TXT",
    })

    assert [type(deserializer) for deserializer in resolved] == [settings_deserializer]


"""Тест: типы, которые не являются словарями, не поддерживаются"""
@pytest.mark.parametrize("value", [None, True, 42, 3.14, "текст", [], object()])
def test_resolve_non_dict_values_return_empty_list(factory, value):
    assert factory.resolve(value) == []


"""Тест: фабрика принимает любой словарь без исключений"""
@pytest.mark.parametrize("value", [{}, {"unknown": 1}, {"name": "Без типа"}])
def test_resolve_accepts_any_dict(factory, value):
    resolved = factory.resolve(value)

    assert isinstance(resolved, list)

    for deserializer in resolved:
        assert deserializer.is_supported(value)


"""Тест: каждый вызов создаёт новые экземпляры десериализаторов"""
def test_resolve_creates_new_instances(factory):
    first = factory.resolve({"name": "Бакалея"})
    second = factory.resolve({"name": "Бакалея"})

    assert first[0] is not second[0]



