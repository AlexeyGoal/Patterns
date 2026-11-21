from Src.Logics.entity_service import entity_service
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.recipe_item_model import recipe_item_model
from Src.Models.recipe_model import recipe_model


COLLECTIONS = {
    "storage_model": "storages",
    "range_model": "ranges",
    "nomenclature_model": "nomenclatures",
    "nomenclature_group_model": "groups",
    "recipe_model": "recipes",
}


class FakeStorage:
    """Минимальное хранилище для проверки обхода объектного графа."""

    def __init__(self):
        self.storages = {}
        self.ranges = {}
        self.nomenclatures = {}
        self.groups = {}
        self.recipes = {}


def make_service(*items):
    storage = FakeStorage()

    for item in items:
        collection = getattr(storage, COLLECTIONS[type(item).__name__])
        collection[item.id] = item

    return entity_service(storage)


def test_group_reference_is_found_in_object_graph():
    """Номенклатура ссылается на группу объектом, а не JSON-полем."""

    group = nomenclature_group_model("Группа")
    unit = range_model("грамм", 1)
    nomenclature = nomenclature_model("Мука", "Мука полная", group, unit)

    service = make_service(group, unit, nomenclature)
    dependents = service._find_dependents("group", group)

    assert [(entity_type, item.id) for entity_type, item in dependents] == [
        ("nomenclature", nomenclature.id)
    ]


def test_embedded_recipe_item_reference_is_found():
    """Ссылка внутри встроенной позиции рецепта видна при обходе графа."""

    unit = range_model("грамм", 1)
    recipe = recipe_model("Суп", "Описание")
    recipe.add_item(recipe_item_model("Мука", 100, unit))

    service = make_service(unit, recipe)
    dependents = service._find_dependents("range", unit)

    assert [(entity_type, item.id) for entity_type, item in dependents] == [
        ("recipe", recipe.id)
    ]


def test_transitive_sub_recipe_reference_is_found():
    """Рецепт, ссылающийся на подрецепт, тоже зависит от его единицы измерения."""

    unit = range_model("грамм", 1)

    sub_recipe = recipe_model("Соус", "Описание")
    sub_recipe.add_item(recipe_item_model("Мука", 10, unit))

    main_recipe = recipe_model("Блюдо", "Описание")
    main_recipe.add_sub_recipe(sub_recipe)

    service = make_service(unit, sub_recipe, main_recipe)
    dependents = service._find_dependents("range", unit)

    assert {item.id for _, item in dependents} == {sub_recipe.id, main_recipe.id}


def test_cyclic_range_references_do_not_loop():
    """Обход объектного графа защищен от циклов базовых единиц измерения."""

    first = range_model("первая", 1)
    second = range_model("вторая", 2)
    first.base_range = second
    second.base_range = first

    service = make_service(first, second)
    dependents = service._find_dependents("range", first)

    assert [(entity_type, item.id) for entity_type, item in dependents] == [
        ("range", second.id)
    ]
