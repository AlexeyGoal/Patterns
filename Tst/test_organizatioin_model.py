import pytest
from Src.Core.exception import arguments_exception
from Src.Models.organization_model import organization_model

"""Тест успешного создания организации с 10-значным ИНН"""
def test_success_organization_model_inn_10_digits():
   
    org = organization_model("Ромашка", "1234567890", "044525225", "40702810938000012345", "ООО")

    assert org.name == "Ромашка"
    assert org.inn == "1234567890"
    assert org.bik == "044525225"
    assert org.account == "40702810938000012345"
    assert org.ownership_form == "ООО"

"""Тест успешного создания организации с 12-значным ИНН"""
def test_success_organization_model_inn_12_digits():
    
    org = organization_model("Иванов", "123456789012", "044525225", "40802810938000012345", "ИП")

    assert org.inn == "123456789012"
    assert org.ownership_form == "ИП"


"""Тест выброс argument_exception при некорректной длине ИНН"""
def test_argument_exception_organization_model_invalid_inn_length():
    
    with pytest.raises(arguments_exception):
        organization_model("Ромашка", "12345678", "044525225", "40702810938000012345", "ООО")


"""Тест выброса argument_exception при наличии букв в ИНН."""
def test_argument_exception_organization_model_inn_with_letters():
    
    with pytest.raises(arguments_exception):
        organization_model("Ромашка", "123456789A", "044525225", "40702810938000012345", "ООО")


"""Тест выброса argument_exception при передаче ИНН как числа int."""
def test_argument_exception_organization_model_inn_as_int():
    
    with pytest.raises(arguments_exception):
        organization_model("Ромашка", 1234567890, "044525225", "40702810938000012345", "ООО")


"""Тест выброса argument_exception при некорректной длине БИК"""
def test_argument_exception_organization_model_invalid_bik():
    
    with pytest.raises(arguments_exception):
        organization_model("Ромашка", "1234567890", "1234567", "40702810938000012345", "ООО")


"""Тест выброса argument_exception при некорректной длине счёта"""
def test_argument_exception_organization_model_invalid_account():
    
    with pytest.raises(arguments_exception):
        organization_model("Ромашка", "1234567890", "044525225", "12345", "ООО")


"""Тест выброса argument_exception при форме собственности длиннее 5 символов"""
def test_argument_exception_organization_model_long_ownership_form():
    
    with pytest.raises(arguments_exception):
        organization_model("Ромашка", "1234567890", "044525225", "40702810938000012345", "ДЛИННАЯ")


"""Выброс argument_exception при изменении БИК на невалидный через сеттер"""
def test_argument_exception_organization_model_setter_invalid_bik():

    org = organization_model("Ромашка", "1234567890", "044525225", "40702810938000012345", "ООО")

    
    with pytest.raises(arguments_exception):
        org.bik = "123"