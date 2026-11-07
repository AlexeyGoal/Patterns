import json

import pytest

from Src.Logics.convert_service import convert_service
from Src.Logics.deserialize_service import deserialize_service
from Src.Logics.storage_manager import storage_manager
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.recipe_item_model import recipe_item_model
from Src.Models.recipe_model import recipe_model
from Src.Models.settings_model import settings_model
from Src.Models.storage_model import storage_model


# Фикстура: чистое хранилище с моделями первого старта
@pytest.fixture
def manager():
    if hasattr(storage_manager, "instance"):
        del storage_manager.instance

    settings = settings_model()
    settings.is_first_start = True

    instance = storage_manager()
    assert instance.convert(settings) is True

    yield instance

    if hasattr(storage_manager, "instance"):
        del storage_manager.instance


# Сериализовать модели и прогнать через текст JSON (UUID и даты становятся строками)
def to_json_data(value):
    serialized = convert_service().convert(value)
    text = json.dumps(serialized, ensure_ascii=False, default=str)
    return json.loads(text)


# Восстановить модели из JSON-совместимых данных
def from_json_data(data):
    return deserialize_service().deserialize(data)


# Сравнить единицы измерения с учётом рекурсивной базовой единицы
def assert_range_equal(loaded, source):
    assert isinstance(loaded, range_model)
    assert loaded.id == source.id
    assert loaded.name == source.name
    assert loaded.conversion_factor == source.conversion_factor

    if source.base_range is None:
        assert loaded.base_range is None
    else:
        assert_range_equal(loaded.base_range, source.base_range)


# Сравнить позиции рецепта с учётом вложенных позиций
def assert_recipe_item_equal(loaded, source):
    assert isinstance(loaded, recipe_item_model)
    assert loaded.id == source.id
    assert loaded.name == source.name
    assert loaded.weight == pytest.approx(source.weight)
    assert loaded.type == source.type

    if source.range is None:
        assert loaded.range is None
    else:
        assert loaded.range.id == source.range.id
        assert loaded.range.name == source.range.name

    assert len(loaded.items) == len(source.items)

    for loaded_item, source_item in zip(loaded.items, source.items):
        assert_recipe_item_equal(loaded_item, source_item)

    assert loaded.calculate_weight() == pytest.approx(source.calculate_weight())


# Сравнить рецепты с учётом позиций и вложенных рецептов
def assert_recipe_equal(loaded, source):
    assert isinstance(loaded, recipe_model)
    assert loaded.id == source.id
    assert loaded.name == source.name
    assert loaded.description == source.description
    assert loaded.is_composite == source.is_composite

    assert len(loaded.items) == len(source.items)

    for loaded_item, source_item in zip(loaded.items, source.items):
        assert_recipe_item_equal(loaded_item, source_item)

    assert len(loaded.sub_recipes) == len(source.sub_recipes)

    for loaded_recipe, source_recipe in zip(loaded.sub_recipes, source.sub_recipes):
        assert_recipe_equal(loaded_recipe, source_recipe)

    assert loaded.net_weight == pytest.approx(source.net_weight)
    assert loaded.gross_weight == pytest.approx(source.gross_weight)

    if source.packaging is None:
        assert loaded.packaging is None
    else:
        assert_recipe_item_equal(loaded.packaging, source.packaging)


"""Тест: загруженные единицы измерения совпадают с моделями storage_manager"""
def test_loaded_ranges_equal_storage_manager_models(manager):
    source = list(manager.ranges.values())

    loaded = from_json_data(to_json_data(source))

    assert len(loaded) == len(source)

    for loaded_item, source_item in zip(loaded, source):
        assert_range_equal(loaded_item, source_item)


"""Тест: загруженные группы номенклатуры совпадают с моделями storage_manager"""
def test_loaded_groups_equal_storage_manager_models(manager):
    source = list(manager.groups.values())

    loaded = from_json_data(to_json_data(source))

    assert len(loaded) == len(source)

    for loaded_item, source_item in zip(loaded, source):
        assert isinstance(loaded_item, nomenclature_group_model)
        assert loaded_item.id == source_item.id
        assert loaded_item.name == source_item.name


"""Тест: загруженная номенклатура совпадает с моделями storage_manager"""
def test_loaded_nomenclatures_equal_storage_manager_models(manager):
    source = list(manager.nomenclatures.values())

    loaded = from_json_data(to_json_data(source))

    assert len(loaded) == len(source)

    for loaded_item, source_item in zip(loaded, source):
        assert isinstance(loaded_item, nomenclature_model)
        assert loaded_item.id == source_item.id
        assert loaded_item.name == source_item.name
        assert loaded_item.full_name == source_item.full_name

        assert loaded_item.group.id == source_item.group.id
        assert loaded_item.group.name == source_item.group.name

        assert_range_equal(loaded_item.range, source_item.range)


"""Тест: загруженные склады совпадают с моделями storage_manager"""
def test_loaded_storages_equal_storage_manager_models(manager):
    source = list(manager.storages.values())

    loaded = from_json_data(to_json_data(source))

    assert len(loaded) == len(source)

    for loaded_item, source_item in zip(loaded, source):
        assert isinstance(loaded_item, storage_model)
        assert loaded_item.id == source_item.id
        assert loaded_item.name == source_item.name
        assert loaded_item.address == source_item.address


"""Тест: загруженные рецепты совпадают с моделями storage_manager"""
def test_loaded_recipes_equal_storage_manager_models(manager):
    source = list(manager.recipes.values())

    loaded = from_json_data(to_json_data(source))

    assert len(loaded) == len(source)

    for loaded_item, source_item in zip(loaded, source):
        assert_recipe_equal(loaded_item, source_item)


"""Тест: составной рецепт сохраняет вложенные рецепты после загрузки"""
def test_loaded_composite_recipe_keeps_sub_recipes(manager):
    gram = range_model("грамм", 1)

    soup = recipe_model.create("Суп-лапша домашняя", "Традиционный суп")
    soup.add_item(recipe_item_model.create_ingredient("Курица (тушка)", 500, gram))

    noodles = recipe_model.create("Лапша домашняя", "Полуфабрикат")
    noodles.add_item(recipe_item_model.create_ingredient("Мука пшеничная", 200, gram))
    noodles.add_item(recipe_item_model.create_ingredient("Вода", 100, gram))

    soup.add_sub_recipe(noodles)
    manager.add_recipe(soup)

    loaded = from_json_data(to_json_data(soup))

    assert_recipe_equal(loaded, soup)


"""Тест: JSON-файл загружается в storage_manager и даёт те же модели"""
def test_storage_manager_load_json_equals_generated_models(manager, tmp_path):
    payload = {
        "storages": to_json_data(list(manager.storages.values())),
        "ranges": to_json_data(list(manager.ranges.values())),
        "groups": to_json_data(list(manager.groups.values())),
        "nomenclatures": to_json_data(list(manager.nomenclatures.values())),
        "recipes": to_json_data(list(manager.recipes.values())),
    }

    path = tmp_path / "storage.json"
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    if hasattr(storage_manager, "instance"):
        del storage_manager.instance

    loaded_manager = storage_manager()
    loaded_manager.load(str(path))

    assert loaded_manager.is_initialized is True
    assert len(loaded_manager.storages) == len(manager.storages)
    assert len(loaded_manager.ranges) == len(manager.ranges)
    assert len(loaded_manager.groups) == len(manager.groups)
    assert len(loaded_manager.nomenclatures) == len(manager.nomenclatures)
    assert len(loaded_manager.recipes) == len(manager.recipes)

    for loaded_item, source_item in zip(
        loaded_manager.storages.values(), manager.storages.values()
    ):
        assert loaded_item.id == source_item.id
        assert loaded_item.name == source_item.name
        assert loaded_item.address == source_item.address

    for loaded_item, source_item in zip(
        loaded_manager.ranges.values(), manager.ranges.values()
    ):
        assert_range_equal(loaded_item, source_item)

    for loaded_item, source_item in zip(
        loaded_manager.nomenclatures.values(), manager.nomenclatures.values()
    ):
        assert loaded_item.id == source_item.id
        assert loaded_item.name == source_item.name
        assert loaded_item.group.id == source_item.group.id
        assert_range_equal(loaded_item.range, source_item.range)

    for loaded_item, source_item in zip(
        loaded_manager.recipes.values(), manager.recipes.values()
    ):
        assert_recipe_equal(loaded_item, source_item)
