import json
from pathlib import Path

import pytest

from Src.Core.validator import operation_exception
from Src.Logics.json_deserializer import json_deserializer, JsonDeserializer
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.settings_model import settings_model


"""Тест: JSON-файл загружается и превращается в модель"""
def test_load_json_file_returns_model(tmp_path):
    path = tmp_path / "range.json"
    path.write_text(
        json.dumps({
            "name": "килограмм",
            "conversion_factor": 1000,
            "base_range": {
                "name": "грамм",
                "conversion_factor": 1,
                "base_range": None,
            },
        }, ensure_ascii=False),
        encoding="utf-8",
    )

    result = json_deserializer().load(str(path))

    assert isinstance(result, range_model)
    assert result.name == "килограмм"
    assert result.base_range.name == "грамм"


"""Тест: JSON-строка загружается и превращается в модель"""
def test_loads_json_text_returns_model():
    text = json.dumps({
        "name": "грамм",
        "conversion_factor": 1,
        "base_range": None,
    }, ensure_ascii=False)

    result = json_deserializer().loads(text)

    assert isinstance(result, range_model)
    assert result.name == "грамм"


"""Тест: настройки приложения восстанавливаются из JSON"""
def test_loads_settings_from_json():
    text = json.dumps({
        "is_first_start": True,
        "organization": {
            "name": "Ромашка",
            "inn": "4444444444",
            "bik": "012345678",
            "account": "12345678901234567890",
            "ownership_form": "ООО",
        },
        "boss_name": "Иванов Иван Иванович",
        "account_name": "Петрова Анна Сергеевна",
        "response_format": "TXT",
    }, ensure_ascii=False)

    result = json_deserializer().loads(text)

    assert isinstance(result, settings_model)
    assert result.organization.name == "Ромашка"
    assert result.boss_name == "Иванов Иван Иванович"
    assert result.response_format == "TXT"


"""Тест: выгруженный ранее reference.json восстанавливается в номенклатуру"""
def test_load_reference_json_file_returns_nomenclature():
    path = Path(__file__).resolve().parent.parent / "reference.json"

    result = json_deserializer().load(str(path))

    assert isinstance(result, nomenclature_model)
    assert result.full_name == "Мука пшеничная высший сорт"
    assert result.group.name == "Бакалея"
    assert result.range.name == "килограмм"
    assert result.range.base_range.name == "грамм"


"""Тест: отсутствующий файл приводит к operation_exception"""
def test_load_missing_file_raises_exception(tmp_path):
    with pytest.raises(operation_exception):
        json_deserializer().load(str(tmp_path / "missing.json"))


"""Тест: некорректный JSON приводит к operation_exception"""
def test_loads_invalid_json_raises_exception():
    with pytest.raises(operation_exception):
        json_deserializer().loads("{not valid json")


