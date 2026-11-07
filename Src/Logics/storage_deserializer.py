from Src.Logics.entity_deserializer import entity_deserializer
from Src.Models.storage_model import storage_model


"""
Десериализатор склада
"""
class storage_deserializer(entity_deserializer):

    """Проверить, что словарь содержит поля склада"""
    @staticmethod
    def is_supported(data: object) -> bool:
        return isinstance(data, dict) and "address" in data


    """Создать склад"""
    def create_model(self, data: dict) -> storage_model:
        return storage_model(data.get("name", ""), data.get("address", ""))


StorageDeserializer = storage_deserializer
