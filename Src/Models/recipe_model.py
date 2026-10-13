from Src.Core.entity import entity
from Src.Core.exception import arguments_exception
from Src.Models.recipe_item_model import recipe_item_model, recipe_item_type
from Src.Models.range_model import range_model


"""Модель технологической карты (рецепта)"""
class recipe_model(entity):

    """Конструктор рецепта"""
    def __init__(self, name="", description=""):

        super().__init__()
        self.name = name
        self.description = description
        self.__items = []
        self.__sub_recipes = []


    """Геттер описания рецепта"""
    @property
    def description(self):
        return self.__description


    """Сеттер описания рецепта"""
    @description.setter
    def description(self, value):

        if not isinstance(value, str):
            raise arguments_exception("description", "description must be str")

        self.__description = value.strip()


    """Геттер списка позиций рецепта"""
    @property
    def items(self):
        return list(self.__items)


    """Геттер списка ингредиентов рецепта"""
    @property
    def ingredients(self):
        return [item for item in self.__items if item.type == recipe_item_type.INGREDIENT]


    """Геттер списка полуфабрикатов рецепта"""
    @property
    def semi_finished_products(self):
        return [item for item in self.__items if item.type == recipe_item_type.SEMI_FINISHED]


    """Геттер упаковки рецепта"""
    @property
    def packaging(self):
        for item in self.__items:
            if item.type == recipe_item_type.PACKAGING:
                return item
        return None


    """Сеттер упаковки рецепта"""
    @packaging.setter
    def packaging(self, value):

        if value is not None and not isinstance(value, recipe_item_model):
            raise arguments_exception("packaging", "packaging should be of the type recipe_item_model")

        if value is not None and value.type != recipe_item_type.PACKAGING:
            raise arguments_exception("packaging", "packaging should have type PACKAGING")

        for i, item in enumerate(self.__items):
            if item.type == recipe_item_type.PACKAGING:
                self.__items.pop(i)
                break

        if value is not None:
            self.__items.append(value)


    """Геттер списка вложенных рецептов"""
    @property
    def sub_recipes(self):
        return list(self.__sub_recipes)


    """Флаг составной рецептуры"""
    @property
    def is_composite(self):
        return len(self.__sub_recipes) > 0


    """Добавление позиции в рецепт"""
    def add_item(self, item):

        if not isinstance(item, recipe_item_model):
            raise arguments_exception("item", "item should be of the type recipe_item_model")

        self.__items.append(item)


    """Удаление позиции из рецепта"""
    def remove_item(self, item):

        if item in self.__items:
            self.__items.remove(item)


    """Добавление вложенного рецепта (блюдо в блюде)"""
    def add_sub_recipe(self, recipe):

        if not isinstance(recipe, recipe_model):
            raise arguments_exception("recipe", "recipe should be of the type recipe_model")

        if recipe is self:
            raise arguments_exception("recipe", "recipe cannot contain itself")

        if recipe.__contains_recipe(self):
            raise arguments_exception("recipe", "circular reference detected")

        self.__sub_recipes.append(recipe)


    """Удаление вложенного рецепта"""
    def remove_sub_recipe(self, recipe):

        if recipe in self.__sub_recipes:
            self.__sub_recipes.remove(recipe)


    """Расчёт веса нетто (рекурсивная сумма весов всех ингредиентов, полуфабрикатов и вложенных карт без упаковки)"""
    @property
    def net_weight(self):

        total = 0.0

        for item in self.__items:
            if item.type in (recipe_item_type.INGREDIENT, recipe_item_type.SEMI_FINISHED):
                total += item.calculate_weight()

        for sub in self.__sub_recipes:
            total += sub.net_weight

        return total


    """Расчёт веса брутто (нетто плюс вес упаковки)"""
    @property
    def gross_weight(self):

        gross = self.net_weight

        packaging = self.packaging
        if packaging is not None:
            gross += packaging.calculate_weight()

        return gross


    """Проверка наличия рецепта в поддереве (защита от циклов)"""
    def __contains_recipe(self, target):

        if self == target:
            return True

        for sub in self.__sub_recipes:
            if sub.__contains_recipe(target):
                return True

        return False


    """Фабричный метод - создать рецепт"""
    @staticmethod
    def create(name="", description=""):
        return recipe_model(name, description)


    """Фабричный метод - создать рецепт «Суп-лапша домашняя» при первом старте"""
    @staticmethod
    def create_first_start_recipe():

        gram = range_model("грамм", 1)
        piece = range_model("штука", 1)

        noodles = recipe_item_model.create_semi_finished("Лапша домашняя (полуфабрикат)", 0, gram)
        noodles.add_item(recipe_item_model.create_ingredient("Мука пшеничная", 200, gram))
        noodles.add_item(recipe_item_model.create_ingredient("Вода", 100, gram))
        noodles.add_item(recipe_item_model.create_ingredient("Яйца куриные", 50, gram))
        noodles.add_item(recipe_item_model.create_ingredient("Соль пищевая мелкая", 5, gram))

        items = [
            recipe_item_model.create_ingredient("Курица (тушка)", 900, gram),
            recipe_item_model.create_ingredient("Морковь", 150, gram),
            recipe_item_model.create_ingredient("Лук репчатый", 120, gram),
            recipe_item_model.create_ingredient("Картофель", 400, gram),
            recipe_item_model.create_ingredient("Масло сливочное", 40, gram),
            recipe_item_model.create_ingredient("Соль пищевая мелкая", 30, gram),
            recipe_item_model.create_ingredient("Перец черный молотый", 4, gram),
            recipe_item_model.create_ingredient("Лавровый лист", 2, piece),
            recipe_item_model.create_ingredient("Зелень укропа", 25, gram),
            recipe_item_model.create_ingredient("Сметана 15%", 160, gram),
            noodles,
            recipe_item_model.create_packaging("Порционная тарелка", 400, gram),
        ]

        recipe = recipe_model.create(
            "Суп-лапша домашняя",
            "Традиционный суп-лапша на курином бульоне с домашней лапшой"
        )

        for item in items:
            recipe.add_item(item)

        return recipe