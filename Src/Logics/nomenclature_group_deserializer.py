from Src.Logics.entity_deserializer import entity_deserializer
from Src.Models.nomenclature_group_model import nomenclature_group_model


"""
Десериализатор группы номенклатуры
"""
class nomenclature_group_deserializer(entity_deserializer):

    """Проверить, что словарь содержит только поля группы номенклатуры"""
    @staticmethod
    def is_supported(data: object) -> bool:
        return (
            isinstance(data, dict)
            and "name" in data
            and set(data).issubset({"id", "name"})
        )


    """Создать группу номенклатуры"""
    def create_model(self, data: dict) -> nomenclature_group_model:
        return nomenclature_group_model(data.get("name", ""))


NomenclatureGroupDeserializer = nomenclature_group_deserializer
