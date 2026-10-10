import pytest
from Src.Core.exception import arguments_exception
from Src.Models.recipe_model import recipe_model
from Src.Models.recipe_item_model import recipe_item_model, recipe_item_type
from Src.Models.range_model import range_model
from Src.Logics.recipe_manager import recipe_manager


"""Тест успешного создания рецепта"""
def test_success_recipe_model_creation():

    recipe = recipe_model("Борщ классический", "Традиционный борщ")

    assert recipe.name == "Борщ классический"
    assert recipe.description == "Традиционный борщ"
    assert recipe.id is not None


"""Тест расчёта веса брутто без позиций"""
def test_gross_weight_empty_recipe():

    recipe = recipe_model("Пустой рецепт")

    assert recipe.gross_weight == 0.0


"""Тест расчёта веса брутто с ингредиентами"""
def test_gross_weight_with_ingredients():

    gram = range_model("грамм", 1)
    recipe = recipe_model("Тестовый рецепт")

    recipe.add_item(recipe_item_model.create_ingredient("Мука", 500, gram))
    recipe.add_item(recipe_item_model.create_ingredient("Сахар", 200, gram))

    assert recipe.gross_weight == 700.0


"""Тест расчёта веса нетто без упаковки"""
def test_net_weight_without_packaging():

    gram = range_model("грамм", 1)
    recipe = recipe_model("Тестовый рецепт")

    recipe.add_item(recipe_item_model.create_ingredient("Мука", 500, gram))

    assert recipe.net_weight == 500.0


"""Тест расчёта веса нетто с упаковкой"""
def test_net_weight_with_packaging():

    gram = range_model("грамм", 1)
    recipe = recipe_model("Тестовый рецепт")

    recipe.add_item(recipe_item_model.create_ingredient("Мука", 500, gram))
    recipe.packaging = recipe_item_model.create_packaging("Контейнер", 50)

    assert recipe.net_weight == 450.0


"""Тест добавления ингредиента и пересчёта брутто"""
def test_add_ingredient_updates_gross_weight():

    gram = range_model("грамм", 1)
    recipe = recipe_model("Тестовый рецепт")

    recipe.add_item(recipe_item_model.create_ingredient("Мука", 300, gram))
    assert recipe.gross_weight == 300.0

    recipe.add_item(recipe_item_model.create_ingredient("Сахар", 200, gram))
    assert recipe.gross_weight == 500.0


"""Тест удаления ингредиента и пересчёта брутто"""
def test_remove_ingredient_updates_gross_weight():

    gram = range_model("грамм", 1)
    recipe = recipe_model("Тестовый рецепт")

    flour = recipe_item_model.create_ingredient("Мука", 300, gram)
    sugar = recipe_item_model.create_ingredient("Сахар", 200, gram)

    recipe.add_item(flour)
    recipe.add_item(sugar)
    assert recipe.gross_weight == 500.0

    recipe.remove_item(flour)
    assert recipe.gross_weight == 200.0


"""Тест добавления полуфабриката и пересчёта брутто"""
def test_add_semi_finished_updates_gross_weight():

    gram = range_model("грамм", 1)
    recipe = recipe_model("Тестовый рецепт")

    semi_finished = recipe_item_model.create_semi_finished("Зажарка овощная", 250, gram)
    recipe.add_item(semi_finished)

    assert recipe.gross_weight == 250.0


"""Тест удаления полуфабриката и пересчёта брутто"""
def test_remove_semi_finished_updates_gross_weight():

    gram = range_model("грамм", 1)
    recipe = recipe_model("Тестовый рецепт")

    semi_finished = recipe_item_model.create_semi_finished("Зажарка овощная", 250, gram)
    recipe.add_item(semi_finished)
    assert recipe.gross_weight == 250.0

    recipe.remove_item(semi_finished)
    assert recipe.gross_weight == 0.0


"""Тест выброса argument_exception при добавлении некорректной позиции"""
def test_argument_exception_recipe_add_invalid_item():

    recipe = recipe_model("Тестовый рецепт")

    with pytest.raises(arguments_exception):
        recipe.add_item("не позиция")


"""Тест выброса argument_exception при установке некорректной упаковки"""
def test_argument_exception_recipe_set_invalid_packaging():

    recipe = recipe_model("Тестовый рецепт")

    with pytest.raises(arguments_exception):
        recipe.packaging = "не упаковка"


"""Тест выброса argument_exception при установке позиции не типа PACKAGING как упаковки"""
def test_argument_exception_recipe_set_wrong_type_as_packaging():

    gram = range_model("грамм", 1)
    recipe = recipe_model("Тестовый рецепт")

    with pytest.raises(arguments_exception):
        recipe.packaging = recipe_item_model.create_ingredient("Мука", 100, gram)


"""Тест выброса argument_exception при создании позиции с отрицательным весом"""
def test_argument_exception_recipe_item_negative_weight():

    gram = range_model("грамм", 1)

    with pytest.raises(arguments_exception):
        recipe_item_model.create_ingredient("Мука", -100, gram)


"""Тест выброса argument_exception при создании позиции с некорректным типом веса"""
def test_argument_exception_recipe_item_invalid_weight_type():

    gram = range_model("грамм", 1)

    with pytest.raises(arguments_exception):
        recipe_item_model.create_ingredient("Мука", "сто", gram)


"""Тест выброса argument_exception при создании позиции с некорректной единицей измерения"""
def test_argument_exception_recipe_item_invalid_range():

    with pytest.raises(arguments_exception):
        recipe_item_model.create_ingredient("Мука", 100, "грамм")


"""Тест выброса argument_exception при создании позиции с некорректным типом"""
def test_argument_exception_recipe_item_invalid_type():

    gram = range_model("грамм", 1)

    with pytest.raises(arguments_exception):
        recipe_item_model("Мука", 100, gram, "неверный_тип")


"""Тест фабричного метода create_ingredient"""
def test_success_recipe_item_create_ingredient():

    gram = range_model("грамм", 1)
    item = recipe_item_model.create_ingredient("Мука", 500, gram)

    assert item.name == "Мука"
    assert item.weight == 500.0
    assert item.range is gram
    assert item.type == recipe_item_type.INGREDIENT


"""Тест фабричного метода create_semi_finished"""
def test_success_recipe_item_create_semi_finished():

    gram = range_model("грамм", 1)
    item = recipe_item_model.create_semi_finished("Зажарка", 250, gram)

    assert item.name == "Зажарка"
    assert item.weight == 250.0
    assert item.range is gram
    assert item.type == recipe_item_type.SEMI_FINISHED


"""Тест фабричного метода create_packaging"""
def test_success_recipe_item_create_packaging():

    gram = range_model("грамм", 1)
    item = recipe_item_model.create_packaging("Контейнер", 50, gram)

    assert item.name == "Контейнер"
    assert item.weight == 50.0
    assert item.range is gram
    assert item.type == recipe_item_type.PACKAGING


"""Тест фильтрации ингредиентов"""
def test_recipe_ingredients_filter():

    gram = range_model("грамм", 1)
    recipe = recipe_model("Тестовый рецепт")

    recipe.add_item(recipe_item_model.create_ingredient("Мука", 500, gram))
    recipe.add_item(recipe_item_model.create_semi_finished("Зажарка", 250, gram))
    recipe.add_item(recipe_item_model.create_packaging("Контейнер", 50, gram))

    assert len(recipe.ingredients) == 1
    assert recipe.ingredients[0].name == "Мука"


"""Тест фильтрации полуфабрикатов"""
def test_recipe_semi_finished_filter():

    gram = range_model("грамм", 1)
    recipe = recipe_model("Тестовый рецепт")

    recipe.add_item(recipe_item_model.create_ingredient("Мука", 500, gram))
    recipe.add_item(recipe_item_model.create_semi_finished("Зажарка", 250, gram))
    recipe.add_item(recipe_item_model.create_packaging("Контейнер", 50, gram))

    assert len(recipe.semi_finished_products) == 1
    assert recipe.semi_finished_products[0].name == "Зажарка"


"""Тест получения упаковки"""
def test_recipe_packaging_getter():

    gram = range_model("грамм", 1)
    recipe = recipe_model("Тестовый рецепт")

    assert recipe.packaging is None

    packaging = recipe_item_model.create_packaging("Контейнер", 50, gram)
    recipe.add_item(packaging)

    assert recipe.packaging is not None
    assert recipe.packaging.name == "Контейнер"


"""Тест загрузки рецепта менеджером"""
def test_recipe_manager_load_recipe():

    manager = recipe_manager()
    manager.load()

    assert manager.is_loaded
    assert manager.recipe is not None
    assert manager.recipe.name == "Суп-лапша домашняя"


"""Тест наличия ингредиентов в загруженном рецепте"""
def test_recipe_manager_ingredients_loaded():

    manager = recipe_manager()
    manager.load()

    assert len(manager.recipe.ingredients) > 0


"""Тест наличия полуфабрикатов в загруженном рецепте"""
def test_recipe_manager_semi_finished_products_loaded():

    manager = recipe_manager()
    manager.load()

    assert len(manager.recipe.semi_finished_products) > 0


"""Тест наличия упаковки в загруженном рецепте"""
def test_recipe_manager_packaging_loaded():

    manager = recipe_manager()
    manager.load()

    assert manager.recipe.packaging is not None


"""Тест расчёта брутто загруженного рецепта"""
def test_recipe_manager_gross_weight():

    manager = recipe_manager()
    manager.load()

    assert manager.recipe.gross_weight > 0


"""Тест расчёта нетто загруженного рецепта"""
def test_recipe_manager_net_weight():

    manager = recipe_manager()
    manager.load()

    assert manager.recipe.net_weight > 0
    assert manager.recipe.net_weight < manager.recipe.gross_weight


"""Тест пересчёта брутто при добавлении ингредиента в загруженный рецепт"""
def test_recipe_manager_add_item_updates_weight():

    manager = recipe_manager()
    manager.load()

    initial_gross = manager.recipe.gross_weight

    gram = range_model("грамм", 1)
    manager.recipe.add_item(recipe_item_model.create_ingredient("Сметана", 100, gram))

    assert manager.recipe.gross_weight == initial_gross + 100


"""Тест пересчёта брутто при удаления позиции из загруженного рецепта"""
def test_recipe_manager_remove_item_updates_weight():

    manager = recipe_manager()
    manager.load()

    initial_gross = manager.recipe.gross_weight
    item_to_remove = manager.recipe.ingredients[0]

    manager.recipe.remove_item(item_to_remove)

    assert manager.recipe.gross_weight == initial_gross - item_to_remove.weight
