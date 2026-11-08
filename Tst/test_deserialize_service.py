import pytest

from Src.Core.exception import arguments_exception
from Src.Logics.deserialize_service import deserialize_service, DeserializeService
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model


# Фикстура: оркестратор десериализации
@pytest.fixture
def service():
    return deserialize_service()


"""Тест: простые значения JSON возвращаются без изменений"""
@pytest.mark.parametrize("value", [None, True, False, 42, 3.14, "текст"])
def test_deserialize_basic_value(service, value):
    assert service.deserialize(value) == value


"""Тест: список обходится рекурсивно"""
def test_deserialize_list_recursively(service):
    data = [
        {"$type": "range", "name": "грамм", "conversion_factor": 1, "base_range": None},
        {"$type": "range", "name": "килограмм", "conversion_factor": 1000, "base_range": None},
    ]

    result = service.deserialize(data)

    assert len(result) == 2
    assert all(isinstance(item, range_model) for item in result)


"""Тест: обычный словарь без модели обходится рекурсивно"""
def test_deserialize_plain_dict_recursively(service):
    data = {"items": [1, 2], "meta": {"count": 2}}

    assert service.deserialize(data) == data


"""Тест: модель восстанавливается по маркеру $type"""
def test_deserialize_model_by_type(service):
    data = {
        "$type": "range_model",
        "id": "0fd16cdf-c5db-4a3d-8b09-d96bca173ebe",
        "name": "килограмм",
        "conversion_factor": 1000,
        "base_range": {
            "$type": "range_model",
            "name": "грамм",
            "conversion_factor": 1,
            "base_range": None,
        },
    }

    result = service.deserialize(data)

    assert isinstance(result, range_model)
    assert str(result.id) == data["id"]
    assert result.base_range.name == "грамм"


"""Тест: номенклатура восстанавливается вместе с группой и единицей измерения"""
def test_deserialize_nomenclature_with_references(service):
    data = {
        "$type": "nomenclature_model",
        "name": "Мука пшеничная",
        "full_name": "Мука пшеничная высший сорт",
        "group": {"$type": "nomenclature_group_model", "name": "Бакалея"},
        "range": {
            "$type": "range_model",
            "name": "килограмм",
            "conversion_factor": 1000,
            "base_range": None,
        },
    }

    result = service.deserialize(data)

    assert isinstance(result, nomenclature_model)
    assert result.group.name == "Бакалея"
    assert result.range.name == "килограмм"


"""Тест: некорректный идентификатор приводит к arguments_exception"""
def test_deserialize_invalid_id_raises_exception(service):
    data = {
        "$type": "range_model",
        "id": "not-a-uuid",
        "name": "грамм",
        "conversion_factor": 1,
        "base_range": None,
    }

    with pytest.raises(arguments_exception):
        service.deserialize(data)


"""Тест: оркестратор принимает фабрику с методом convert"""
def test_deserialize_uses_injected_factory():
    class stub_factory:
        def convert(self, source):
            return {"converted": source}

    service = deserialize_service(stub_factory())

    assert service.deserialize({"value": 1}) == {"converted": {"value": 1}}


"""Тест: алиас DeserializeService указывает на тот же класс"""
def test_alias():
    assert DeserializeService is deserialize_service
