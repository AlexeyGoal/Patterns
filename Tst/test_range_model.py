import pytest
from Src.Core.exception import arguments_exception
from Src.Models.range_model import range_model

"""Тест успешного создание базовой единицы измерения."""
def test_success_range_model_create_base_unit():
   
    gram = range_model("грамм", 1)

    assert gram.name == "грамм"
    assert gram.conversion_factor == 1
    assert gram.base_range is None
    

"""Тест успешного создание производной единицы измерения"""
def test_success_range_model_create_derived_unit():
    
    gram = range_model("грамм", 1)

    kg = range_model("кг", 1000, gram)

    assert kg.name == "кг"
    assert kg.conversion_factor == 1000
    assert kg.base_range is gram
    assert kg.base_range.name == "грамм"

"""Тест корректного пересчёта величин между единицами измерения"""
def test_success_range_model_conversion_calculation():

    gram = range_model("грамм", 1)
    kg = range_model("кг", 1000, gram)
    quantity_kg = 2.5

    quantity_gram = quantity_kg * kg.conversion_factor

    assert quantity_gram == 2500


"""Тест корректного многоуровненого пересчёта"""
def test_success_range_model_chain_conversion():
   
    gram = range_model("грамм", 1)
    kg = range_model("кг", 1000, gram)
    ton = range_model("тонна", 1000, kg)

    quantity_gram = 2 * ton.conversion_factor * kg.conversion_factor

    assert quantity_gram == 2_000_000

"""Тест успешного создания единицы с дробным коэффициентом пересчёта"""
def test_success_range_model_float_conversion_factor():
    
    gram = range_model("грамм", 1)
    mg = range_model("мг", 0.001, gram)

    assert mg.conversion_factor == 0.001
    assert mg.base_range is gram


"""Тест выброса argument_exception при нулевом коэффициенте пересчёта"""
def test_argument_exception_range_model_zero_factor():
    
    with pytest.raises(arguments_exception):
        range_model("ошибка", 0)


"""Тест выброса argument_exception при отрицательном коэффициенте пересчёта"""
def test_argument_exception_range_model_negative_factor():
    
    with pytest.raises(arguments_exception):
        range_model("ошибка", -5)



"""Тест  выброса argument_exception при передаче строки вместо числа"""
def test_argument_exception_range_model_string_factor():

    with pytest.raises(arguments_exception):
        range_model("ошибка", "1000")



"""Тест выброса argument_exception при передаче строки в качестве базовой единицы"""
def test_argument_exception_range_model_invalid_base_type():
    
    with pytest.raises(arguments_exception):
        range_model("кг", 1000, "грамм")