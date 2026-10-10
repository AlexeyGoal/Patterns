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


    """Добавление позиции в рецепт"""
    def add_item(self, item):

        if not isinstance(item, recipe_item_model):
            raise arguments_exception("item", "item should be of the type recipe_item_model")

        self.__items.append(item)


    """Удаление позиции из рецепта"""
    def remove_item(self, item):

        if item in self.__items:
            self.__items.remove(item)


    """Расчёт веса брутто (сумма весов всех ингредиентов и полуфабрикатов)"""
    @property
    def gross_weight(self):

        total = 0.0

        for item in self.__items:
            if item.type in (recipe_item_type.INGREDIENT, recipe_item_type.SEMI_FINISHED):
                total += item.weight

        return total


    """Расчёт веса нетто (вес брутто минус вес упаковки)"""
    @property
    def net_weight(self):

        net = self.gross_weight

        packaging = self.packaging
        if packaging is not None:
            net -= packaging.weight

        return max(net, 0.0)


    """Фабричный метод - создать рецепт"""
    @staticmethod
    def create(name="", description=""):
        return recipe_model(name, description)


    """Фабричный метод - создать рецепт «Суп-лапша домашняя» при первом старте"""
    @staticmethod
    def create_first_start_recipe():

        gram = range_model("грамм", 1)
        piece = range_model("штука", 1)

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
            recipe_item_model.create_semi_finished("Лапша домашняя (полуфабрикат)", 300, gram),
            recipe_item_model.create_packaging("Порционная тарелка", 400, gram),
        ]

        recipe = recipe_model.create(
            "Суп-лапша домашняя",
            "Традиционный суп-лапша на курином бульоне с домашней лапшой"
        )

        for item in items:
            recipe.add_item(item)

        return recipe
