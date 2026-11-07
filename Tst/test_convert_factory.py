import datetime
import uuid

import pytest

from Src.Logics.basic_convertor import basic_convertor
from Src.Logics.convert_factory import convert_factory, ConvertFactory
from Src.Logics.datetime_convertor import datetime_convertor
from Src.Logics.reference_convertor import reference_convertor
from Src.Models.range_model import range_model


# Фикстура: фабрика конвертеров
@pytest.fixture
def factory():
    return convert_factory()




"""Тест: для сущности фабрика выбирает конвертор ссылок"""
def test_resolve_entity_returns_reference_convertor(factory):
    resolved = factory.resolve(range_model.create_gram())

    assert [type(convertor) for convertor in resolved] == [reference_convertor]


"""Тест: для даты/времени фабрика выбирает конвертор дат"""
def test_resolve_datetime_returns_datetime_convertor(factory):
    moment = datetime.datetime(2026, 10, 24, 12, 30)

    resolved = factory.resolve(moment)

    assert [type(convertor) for convertor in resolved] == [datetime_convertor]


"""Тест: для простых типов фабрика выбирает конвертор базовых значений"""
@pytest.mark.parametrize("value", ["текст", 42, 3.14])
def test_resolve_basic_value_returns_basic_convertor(factory, value):
    resolved = factory.resolve(value)

    assert [type(convertor) for convertor in resolved] == [basic_convertor]


"""Тест: типы вне поддержки конвертеров дают пустой список"""
@pytest.mark.parametrize("value", [None, True, uuid.uuid4(), object()])
def test_resolve_unsupported_values_return_empty_list(factory, value):
    assert factory.resolve(value) == []


"""Тест: фабрика принимает любой объект любого типа без исключений"""
@pytest.mark.parametrize("value", [
    None, True, 42, 3.14, "текст", [1, 2], {"a": 1}, uuid.uuid4(), object(),
    datetime.datetime(2026, 10, 24, 12, 30),
    range_model.create_gram(),
])
def test_resolve_accepts_any_object(factory, value):
    resolved = factory.resolve(value)

    assert isinstance(resolved, list)

    for convertor in resolved:
        assert convertor.is_supported(value)


"""Тест: каждый вызов создаёт новые экземпляры конверторов"""
def test_resolve_creates_new_instances(factory):
    first = factory.resolve("текст")
    second = factory.resolve("текст")

    assert first[0] is not second[0]


"""Тест: фабрика только подбирает конверторы, сама не конвертирует"""
def test_factory_does_not_convert(factory):
    assert not hasattr(factory, "convert")


"""Тест: алиас ConvertFactory указывает на тот же класс"""
def test_alias():
    assert ConvertFactory is convert_factory
