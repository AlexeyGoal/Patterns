from Src.Logics.entity_deserializer import entity_deserializer
from Src.Models.recipe_item_model import recipe_item_model
from Src.Models.recipe_model import recipe_model


"""
Десериализатор рецепта
"""
class recipe_deserializer(entity_deserializer):

    """Проверить, что словарь содержит поля рецепта, а не позиции рецепта"""
    @staticmethod
    def is_supported(data: object) -> bool:
        if not isinstance(data, dict) or "name" not in data:
            return False

        if "weight" in data or "type" in data:
            return False

        return "description" in data or "items" in data or "sub_recipes" in data


    """Создать рецепт с рекурсивным восстановлением позиций и вложенных рецептов"""
    def create_model(self, data: dict) -> recipe_model:
        recipe = recipe_model.create(
            data.get("name", ""),
            data.get("description", "")
        )

        for item_data in data.get("items") or []:
            item = self._deserialize_value(item_data)
            if isinstance(item, recipe_item_model):
                recipe.add_item(item)

        for sub_recipe_data in data.get("sub_recipes") or []:
            sub_recipe = self._deserialize_value(sub_recipe_data)
            if isinstance(sub_recipe, recipe_model):
                recipe.add_sub_recipe(sub_recipe)

        packaging_data = data.get("packaging")
        if isinstance(packaging_data, dict) and recipe.packaging is None:
            packaging = self._deserialize_value(packaging_data)
            if isinstance(packaging, recipe_item_model):
                recipe.packaging = packaging

        return recipe


RecipeDeserializer = recipe_deserializer
