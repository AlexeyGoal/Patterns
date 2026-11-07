from Src.Logics.entity_deserializer import entity_deserializer
from Src.Models.range_model import range_model


"""
Десериализатор единицы измерения
"""
class range_deserializer(entity_deserializer):

    """Проверить, что словарь содержит поля единицы измерения"""
    @staticmethod
    def is_supported(data: object) -> bool:
        return isinstance(data, dict) and "conversion_factor" in data


    """Создать единицу измерения с рекурсивным восстановлением базовой единицы"""
    def create_model(self, data: dict) -> range_model:
        base_range = self._deserialize_value(data.get("base_range"))

        if base_range is not None and not isinstance(base_range, range_model):
            base_range = None

        return range_model(
            data.get("name", ""),
            data.get("conversion_factor", 1),
            base_range
        )


RangeDeserializer = range_deserializer
