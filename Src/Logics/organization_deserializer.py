from Src.Logics.entity_deserializer import entity_deserializer
from Src.Models.organization_model import organization_model


"""
Десериализатор организации
"""
class organization_deserializer(entity_deserializer):

    """Проверить, что словарь содержит реквизиты организации"""
    @staticmethod
    def is_supported(data: object) -> bool:
        if not isinstance(data, dict):
            return False

        return any(field in data for field in ("inn", "bik", "account", "ownership_form"))


    """Создать организацию"""
    def create_model(self, data: dict) -> organization_model:
        return organization_model(
            data.get("name", ""),
            data.get("inn", ""),
            data.get("bik", ""),
            data.get("account", ""),
            data.get("ownership_form", "")
        )


OrganizationDeserializer = organization_deserializer
