import pytest
from Src.Core.exception import max_length_exception
from Src.Models.nomenclature_group_model import nomenclature_group_model

"""Тест успешного создания группы номенклатуры"""
def test_success_nomenclature_group_model_creation():

    group = nomenclature_group_model("Мясо")

    assert group.name == "Мясо"
    assert group.id is not None

"""Тест выброса max_length_exception при имени длиннее 50 символов"""
def test_argument_exception_nomenclature_group_model_long_name():
        
    long_name = "А" * 51

    with pytest.raises(max_length_exception):
        nomenclature_group_model(long_name)

"""Тест успешного создания группы с именем в 50 символов"""
def test_success_nomenclature_group_model_boundary_50_chars():
    
    exact_name = "А" * 50
    group = nomenclature_group_model(exact_name)

    assert len(group.name) == 50