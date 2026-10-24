import datetime
import json
import uuid
from pathlib import Path

import pytest

from Src.Logics.basic_convertor import basic_convertor
from Src.Logics.datetime_convertor import datetime_convertor
from Src.Logics.reference_convertor import reference_convertor
from Src.Models.nomenclature_model import nomenclature_model


"""
Выгрузка JSON-файлов 
"""

OUT_DIR = Path(__file__).resolve().parent.parent


"""JSON не сериализует UUID и datetime - приводим их к строкам"""
def json_default(value):

    if isinstance(value, (datetime.datetime, datetime.date, datetime.time)):
        return value.isoformat()

    return str(value)


"""Сохранить данные в JSON-файл (UTF-8, кириллица без экранирования)"""
def save_json(path: Path, data) -> None:

    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2, default=json_default)


"""Прочитать выгруженный файл обратно как JSON"""
def load_json(path: Path) -> dict:

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


# Фикстура: выгружает три JSON-файла один раз на модуль
@pytest.fixture(scope="module")
def exported() -> dict:

    moment = datetime.datetime(2026, 10, 24, 12, 30)
    flour = nomenclature_model.create_flour()

    # basic.json - поддерживаемые простые типы: str, int, float
    basic = basic_convertor()
    basic_data = {}
    for sample in ("Мука пшеничная", 42, 3.14):
        basic_data.update(basic.Convert(sample))

    paths = {
        "basic": OUT_DIR / "basic.json",
        "datetime": OUT_DIR / "datetime.json",
        "reference": OUT_DIR / "reference.json",
    }

    save_json(paths["basic"], basic_data)
    save_json(paths["datetime"], datetime_convertor().Convert(moment))
    save_json(paths["reference"], reference_convertor().Convert(flour))

    return {"paths": paths, "moment": moment, "flour": flour}


"""Тест: basic.json выгружен и содержит поддерживаемые простые типы"""
def test_basic_json_exported(exported):
    data = load_json(exported["paths"]["basic"])

    assert data == {"str": "Мука пшеничная", "int": 42, "float": 3.14}


"""Тест: datetime.json выгружен и содержит дату/время в ISO-формате"""
def test_datetime_json_exported(exported):
    data = load_json(exported["paths"]["datetime"])

    assert data == {"datetime": exported["moment"].isoformat()}


"""Тест: reference.json выгружен - поля справочника, ссылки в виде строковых id"""
def test_reference_json_exported(exported):
    data = load_json(exported["paths"]["reference"])
    flour = exported["flour"]

    assert data["name"] == "Мука пшеничная"
    assert data["full_name"] == "Мука пшеничная высший сорт"
    assert uuid.UUID(data["id"]) == flour.id
    assert uuid.UUID(data["group"]) == flour.group.id
    assert uuid.UUID(data["range"]) == flour.range.id


"""Тест: каждый файл лежит в корне проекта, валиден и без экранированной кириллицы"""
@pytest.mark.parametrize("name", ["basic", "datetime", "reference"])
def test_exported_file_is_valid_json(exported, name):
    path = exported["paths"][name]
    text = path.read_text(encoding="utf-8")

    data = json.loads(text)

    assert path.parent == OUT_DIR
    assert isinstance(data, dict)
    assert "\\u" not in text
