from Src.Logics.entity_deserializer import entity_deserializer
from Src.Models.range_model import range_model
from Src.Models.recipe_item_model import recipe_item_model


"""
Десериализатор позиции рецепта
"""
class recipe_item_deserializer(entity_deserializer):

    """Проверить, что словарь содержит поля позиции рецепта"""
    @staticmethod
    def is_supported(data: object) -> bool:
        if not isinstance(data, dict):
            return False

        return "weight" in data and "type" in data


    """Создать позицию рецепта с рекурсивным восстановлением вложенных позиций"""
    def create_model(self, data: dict) -> recipe_item_model:
        unit = self._deserialize_value(data.get("range"))

        if unit is not None and not isinstance(unit, range_model):
            unit = None

        item = recipe_item_model(
            data.get("name", ""),
            data.get("weight", 0),
            unit,
            data.get("type")
        )

        for child in data.get("items") or []:
            child_item = self._deserialize_value(child)
            if isinstance(child_item, recipe_item_model):
                item.add_item(child_item)

        return item


RecipeItemDeserializer = recipe_item_deserializer
