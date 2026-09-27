import pytest
from Src.Core.exception import arguments_exception
from Src.Models.storage_model import storage_model

"""Тест успешного создания склада"""
def test_success_storage_model_creation():

    storage = storage_model("Основной склад")

    assert storage.name == "Основной склад"
    assert storage.id is not None
    assert storage.address == ""



"""Тест успешного создания склада с указанием адреса"""
def test_success_storage_model_creation_with_address():
    
    storage = storage_model("Основной склад", "г. Москва, ул. Мира, д. 10")

    assert storage.name == "Основной склад"
    assert storage.address == "г. Москва, ул. Мира, д. 10"



"""Тест выброса argument_exception при передаче нестрокового адреса"""
def test_argument_exception_storage_model_invalid_address_type():
    
    with pytest.raises(arguments_exception):
        storage_model("Основной склад", 12345)



"""Тест выброса argument_exception при пустом имени склада"""
def test_argument_exception_storage_model_empty_name():
    
    with pytest.raises(arguments_exception):
        storage_model("")



"""Тест выброса argument_exception при имени из одних пробелов"""
def test_argument_exception_storage_model_whitespace_name():
    
    with pytest.raises(arguments_exception):
        storage_model("   ")



"""Тест сравнения модели со строкой возвращает False без ошибки"""
def test_false_eq_storage_model_compare_with_string():
    
    storage = storage_model("Основной склад")

    assert storage != "Основной склад"
    assert storage != 123



"""Тест два склада с одинаковым именем, но разными ID — не равны"""
def test_false_eq_storage_model_same_name_different_id():
    
    storage1 = storage_model("Основной склад")
    storage2 = storage_model("Основной склад")

    assert storage1 != storage2
    assert storage1.name == storage2.name