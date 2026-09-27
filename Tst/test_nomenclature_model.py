import pytest
from Src.Core.exception import arguments_exception, max_length_exception
from Src.Models.range_model import range_model
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.nomenclature_model import nomenclature_model

 
"""Тест успешного создания номенклатуры с полным набором параметров"""
def test_success_nomenclature_model_full_creation():
   
    gram = range_model("грамм", 1)
    group = nomenclature_group_model("Мясо")

    item = nomenclature_model("Говядина", "Говядина охлаждённая, вырезка", group, gram)

    assert item.name == "Говядина"
    assert item.full_name == "Говядина охлаждённая, вырезка"
    assert item.group is group
    assert item.range is gram


"""Тест успешного создания номенклатуры с полным именем ровно в 255 символов"""
def test_success_nomenclature_model_boundary_255_full_name():
    
    gram = range_model("грамм", 1)
    group = nomenclature_group_model("Мясо")
    long_full_name = "А" * 255

    item = nomenclature_model("Говядина", long_full_name, group, gram)

    assert len(item.full_name) == 255

"""Тест выброса max_length_exception при полном наименовании длиннее 255 символов"""
def test_argument_exception_nomenclature_model_full_name_too_long():
    
    gram = range_model("грамм", 1)
    group = nomenclature_group_model("Мясо")
    too_long_name = "А" * 256

    with pytest.raises(max_length_exception):
        nomenclature_model("Говядина", too_long_name, group, gram)

"""Тест выброса argument_exception при пустом полном наименовании"""
def test_argument_exception_nomenclature_model_empty_full_name():
    
    gram = range_model("грамм", 1)
    group = nomenclature_group_model("Мясо")

    with pytest.raises(arguments_exception):
        nomenclature_model("Говядина", "", group, gram)


"""Тест выброса argument_exception при передаче строки вместо объекта группы."""
def test_argument_exception_nomenclature_model_invalid_group_type():
    
    gram = range_model("грамм", 1)

    with pytest.raises(arguments_exception):
        nomenclature_model("Говядина", "Говядина полное", "Мясо", gram)



"""Тест выброса argument_exception при передаче строки вместо объекта единицы измерения."""
def test_argument_exception_nomenclature_model_invalid_range_type():

    group = nomenclature_group_model("Мясо")

    with pytest.raises(arguments_exception):
        nomenclature_model("Говядина", "Говядина полное", group, "грамм")