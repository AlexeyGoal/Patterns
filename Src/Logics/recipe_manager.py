from Src.Core.abstract_manager import abstract_manager
from Src.Core.validator import operation_exception
from Src.Models.recipe_model import recipe_model


# Менеджер рецептов
class recipe_manager(abstract_manager):

    _recipe: recipe_model = None
    __is_loaded: bool = False

    # Singleton
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(recipe_manager, cls).__new__(cls)
        return cls.instance

    # Генерация рецепта "Суп-лапша домашняя" при первом старте
    def load(self, file_name: str = "") -> None:

        try:
            self._recipe = self._generate_recipe()
            self.__is_loaded = True

        except Exception as ex:
            raise operation_exception(
                f"Ошибка при генерации рецепта: {ex}"
            ) from ex

    # Флаг успешности генерации рецепта
    @property
    def is_loaded(self) -> bool:
        return self.__is_loaded

    # Объект рецепта recipe_model
    @property
    def recipe(self) -> recipe_model:
        return self._recipe

    # Генерация рецепта "Суп-лапша домашняя" при первом старте
    def _generate_recipe(self) -> recipe_model:
        return recipe_model.create_first_start_recipe()
