import pytest 
from Src.Core.entity import entity 
from Src.Core.exception import arguments_exception
import uuid
"""Тестовая сущность, наследующая базовый класс entity для проверки его функциональности"""
class test_entity(entity):
    pass 


"""Тест который проверяет что при инициализации объекта свойство id автоматически заполняется и не равно None"""
def test_abstract_model_get_id_not_null():
    ent = test_entity()

    result = ent.id
    assert result is not None 

"""Тест для проверки уникальности id для разных экземпляров сущности"""
def test_unique_id():
    
    ent1 = test_entity()
    ent2 = test_entity()
    
    assert ent1.id != ent2.id

"""Тест для проверки сравнения сущностей, сущности одного типа с одинаковым идентификатором считаются равными"""
def test_same_id():
    ent1 = test_entity()
    ent2 = test_entity()
    
    new_id = uuid.uuid4()

    ent1.id = new_id
    ent2.id = new_id

    assert ent1 == ent2


"""Тест для проверки вызова arguments_exception при пустом name"""
def test_empty_name_exception():
    ent = test_entity()
    with pytest.raises(arguments_exception):
        ent.name = ""

"""Тест для проверки вызова arguments_exception когда name None"""
def test_none_name_exception():
    ent = test_entity()
    with pytest.raises(arguments_exception):
        ent.name = None

   



