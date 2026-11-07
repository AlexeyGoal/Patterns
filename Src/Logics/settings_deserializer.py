from Src.Logics.entity_deserializer import entity_deserializer
from Src.Models.organization_model import organization_model
from Src.Models.settings_model import settings_model


"""
Десериализатор настроек приложения
"""
class settings_deserializer(entity_deserializer):

    """Проверить, что словарь содержит поля настроек"""
    @staticmethod
    def is_supported(data: object) -> bool:
        if not isinstance(data, dict):
            return False

        return any(field in data for field in (
            "is_first_start", "response_format", "boss_name", "account_name"
        ))


    """Создать настройки приложения"""
    def create_model(self, data: dict) -> settings_model:
        settings = settings_model()

        organization = self._deserialize_value(data.get("organization"))
        if isinstance(organization, organization_model):
            settings.organization = organization

        for field in ("boss_name", "account_name"):
            value = data.get(field)
            if value is not None and str(value).strip():
                setattr(settings, field, str(value).strip())

        if "is_first_start" in data:
            settings.is_first_start = bool(data.get("is_first_start"))

        if "response_format" in data:
            settings.response_format = str(data.get("response_format"))

        return settings


SettingsDeserializer = settings_deserializer
