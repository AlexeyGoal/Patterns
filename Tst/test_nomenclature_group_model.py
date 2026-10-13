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


"""Тест фабричного метода create_grocery"""
def test_success_nomenclature_group_model_create_grocery():

    group = nomenclature_group_model.create_grocery()

    assert group.name == "Бакалея"
    assert group.id is not None


"""Тест фабричного метода create_dairy"""
def test_success_nomenclature_group_model_create_dairy():

    group = nomenclature_group_model.create_dairy()

    assert group.name == "Молочные продукты"
    assert group.id is not None


"""Тест фабричного метода create_dishes"""
def test_success_nomenclature_group_model_create_dishes():

    group = nomenclature_group_model.create_dishes()

    assert group.name == "Блюда"
    assert group.id is not None


"""Тест фабричного метода create_packaging"""
def test_success_nomenclature_group_model_create_packaging():

    group = nomenclature_group_model.create_packaging()

    assert group.name == "Упаковка"
    assert group.id is not None


"""Тест фабричного метода create_meat"""
def test_success_nomenclature_group_model_create_meat():

    group = nomenclature_group_model.create_meat()

    assert group.name == "Мясные продукты"
    assert group.id is not None


"""Тест фабричного метода create_vegetables"""
def test_success_nomenclature_group_model_create_vegetables():

    group = nomenclature_group_model.create_vegetables()

    assert group.name == "Овощи"
    assert group.id is not None


"""Тест фабричного метода create_semi_finished"""
def test_success_nomenclature_group_model_create_semi_finished():

    group = nomenclature_group_model.create_semi_finished()

    assert group.name == "Полуфабрикаты"
    assert group.id is not None