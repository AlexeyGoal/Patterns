import json

import pytest

from Src.Logics.settings_manager import settings_manager
from Src.Models.organization_model import organization_model
from Src.Models.settings_model import settings_model


@pytest.fixture
def manager():
    """Менеджер настроек с восстановлением настроек по умолчанию после теста."""

    instance = settings_manager()
    yield instance
    instance.load()


def write_settings(path, payload):
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return path


"""Тест: настройки без $type загружаются через общий механизм десериализации"""
def test_load_plain_settings_through_deserializer(manager, tmp_path):
    path = write_settings(
        tmp_path / "settings_plain.json",
        {
            "is_first_start": False,
            "organization": {
                "name": "Тестовая организация",
                "inn": "1234567890",
                "bik": "123456789",
                "account": "12345678901234567890",
                "ownership_form": "ООО",
            },
            "boss_name": "Директор Тестовый",
            "account_name": "Бухгалтер Тестовый",
            "response_format": "CSV",
        },
    )

    manager.load(str(path))

    assert manager.is_loaded is True
    assert isinstance(manager.settings, settings_model)
    assert isinstance(manager.settings.organization, organization_model)
    assert manager.settings.organization.name == "Тестовая организация"
    assert manager.settings.boss_name == "Директор Тестовый"
    assert manager.settings.response_format == "CSV"


"""Тест: типизированный файл настроек восстанавливается штатной фабрикой"""
def test_load_typed_settings_through_deserializer(manager, tmp_path):
    path = write_settings(
        tmp_path / "settings_typed.json",
        {
            "$type": "settings_model",
            "is_first_start": True,
            "organization": {
                "$type": "organization_model",
                "name": "Ромашка",
                "inn": "4444444444",
                "bik": "012345678",
                "account": "12345678901234567890",
                "ownership_form": "ООО",
            },
            "boss_name": "Иванов Иван Иванович",
            "account_name": "Петрова Анна Сергеевна",
            "response_format": "TXT",
        },
    )

    manager.load(str(path))

    assert manager.is_loaded is True
    assert manager.settings.organization.name == "Ромашка"
    assert manager.settings.response_format == "TXT"


"""Тест: convert повторно применяет общий механизм десериализации"""
def test_convert_rebuilds_settings_model(manager, tmp_path):
    path = write_settings(
        tmp_path / "settings_convert.json",
        {
            "is_first_start": False,
            "organization": {
                "name": "Организация",
                "inn": "1234567890",
                "bik": "123456789",
                "account": "12345678901234567890",
                "ownership_form": "ООО",
            },
            "boss_name": "Руководитель",
            "account_name": "Бухгалтер",
            "response_format": "XML",
        },
    )

    manager.load(str(path))
    previous_settings = manager.settings

    assert manager.convert() is True
    assert manager.settings is not previous_settings
    assert manager.settings.response_format == "XML"
