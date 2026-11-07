import pytest
from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.exception import arguments_exception
from Src.Logics.basic_convertor import basic_convertor, BasicConvertor



"""Тест: целое число конвертируется в словарь с ключом int"""
def test_convert_int_returns_dict_with_type_name():
    convertor = basic_convertor()

    result = convertor.convert(42)

    assert isinstance(result, dict)
    assert result == {"int": 42}


"""Тест: дробное число конвертируется в словарь с ключом float"""
def test_convert_float_returns_dict_with_type_name():
    convertor = basic_convertor()

    result = convertor.convert(3.14)

    assert result == {"float": 3.14}


"""Тест: строка конвертируется в словарь с ключом str"""
def test_convert_str_returns_dict_with_type_name():
    convertor = basic_convertor()

    result = convertor.convert("Мука")

    assert result == {"str": "Мука"}


"""Тест: значение сохраняется в словаре без изменений"""
def test_convert_keeps_source_value():
    convertor = basic_convertor()

    result = convertor.convert(0)

    assert result["int"] == 0


"""Тест: bool не поддерживается, хотя и является подклассом int"""
def test_convert_bool_raises_exception():
    convertor = basic_convertor()

    with pytest.raises(arguments_exception):
        convertor.convert(True)


"""Тест: составные типы не поддерживаются и вызывают исключение"""
@pytest.mark.parametrize("source", [None, [1, 2], {"a": 1}, object()])
def test_convert_unsupported_types_raises_exception(source):
    convertor = basic_convertor()

    with pytest.raises(arguments_exception):
        convertor.convert(source)


"""Тест: is_supported возвращает True только для простых типов"""
def test_is_supported_simple_types():
    assert basic_convertor.is_supported(1) is True
    assert basic_convertor.is_supported(1.5) is True
    assert basic_convertor.is_supported("text") is True


"""Тест: is_supported возвращает False для bool и составных типов"""
def test_is_supported_unsupported_types():
    assert basic_convertor.is_supported(True) is False
    assert basic_convertor.is_supported(None) is False
    assert basic_convertor.is_supported([1]) is False


"""Тест: алиас BasicConvertor указывает на тот же класс"""
def test_alias():
    assert BasicConvertor is basic_convertor
