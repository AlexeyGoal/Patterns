from Src.Logics.entity_deserializer import entity_deserializer
from Src.Models.nomenclature_model import nomenclature_model


"""
Десериализатор номенклатуры
"""
class nomenclature_deserializer(entity_deserializer):

    """Проверить, что словарь содержит поля номенклатуры"""
    @staticmethod
    def is_supported(data: object) -> bool:
        if not isinstance(data, dict):
            return False

        return "full_name" in data or ("group" in data and "range" in data)


    """Создать номенклатуру с рекурсивным восстановлением группы и единицы измерения"""
    def create_model(self, data: dict) -> nomenclature_model:
        group = self._deserialize_value(self._require(data, "group"))
        unit = self._deserialize_value(self._require(data, "range"))

        return nomenclature_model(
            data.get("name", ""),
            data.get("full_name", ""),
            group,
            unit
        )


NomenclatureDeserializer = nomenclature_deserializer
