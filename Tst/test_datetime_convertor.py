import datetime
import pytest
from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.exception import arguments_exception
from Src.Logics.datetime_convertor import datetime_convertor, DatetimeConvertor




"""Тест: значение типа DateTime конвертируется в словарь с ключом datetime"""
def test_convert_datetime_returns_dict_with_type_name():
    convertor = datetime_convertor()
    value = datetime.datetime(2026, 10, 24, 15, 30, 0)

    result = convertor.Convert(value)

    assert isinstance(result, dict)
    assert result == {"datetime": value}


"""Тест: значение сохраняется в словаре без изменений"""
def test_convert_keeps_source_value():
    convertor = datetime_convertor()
    value = datetime.datetime(2026, 1, 1, 0, 0, 0)

    result = convertor.Convert(value)

    assert result["datetime"] == value


"""Тест: дата без времени (date) не поддерживается, поддерживается только DateTime"""
def test_convert_date_not_supported():
    convertor = datetime_convertor()

    with pytest.raises(arguments_exception):
        convertor.Convert(datetime.date(2026, 10, 24))


"""Тест: время без даты (time) не поддерживается"""
def test_convert_time_not_supported():
    convertor = datetime_convertor()

    with pytest.raises(arguments_exception):
        convertor.Convert(datetime.time(15, 30, 0))


"""Тест: простые типы не поддерживаются и вызывают исключение"""
@pytest.mark.parametrize("source", [42, 3.14, "2026-10-24", None, [1], object()])
def test_convert_unsupported_types_raises_exception(source):
    convertor = datetime_convertor()

    with pytest.raises(arguments_exception):
        convertor.Convert(source)


"""Тест: is_supported возвращает True только для типа DateTime"""
def test_is_supported_datetime():
    assert datetime_convertor.is_supported(datetime.datetime.now()) is True


"""Тест: is_supported возвращает False для иных типов"""
def test_is_supported_unsupported_types():
    assert datetime_convertor.is_supported(datetime.date.today()) is False
    assert datetime_convertor.is_supported(datetime.time(1, 1, 1)) is False
    assert datetime_convertor.is_supported(42) is False
    assert datetime_convertor.is_supported(None) is False


"""Тест: алиас DatetimeConvertor указывает на тот же класс"""
def test_alias():
    assert DatetimeConvertor is datetime_convertor
