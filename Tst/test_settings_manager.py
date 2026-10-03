import pytest
from Src.Core.validator import operation_exception
from Src.Logics.settings_manager import settings_manager
from Src.Models.settings_model import settings_model
from Src.Models.organization_model import organization_model


# Проверяет, что вызов load с дефолтным файлом settings.json завершается без выброса operation_exception или иных ошибок.
def test_not_raise_settings_manager_load():
    
    manager = settings_manager()
    try:
        manager.load()
    except operation_exception:
        assert False
    except Exception:
        assert False



# После вызова load свойство settings не должно быть None.
def test_not_empty_settings_manager_load():
    
    manager = settings_manager()
    try:
        manager.load()
    except Exception:
        assert False

    assert manager.settings is not None

# Проверяет работу шаблона Singleton
def test_equal_settings_manager_create():
    
    instance1 = settings_manager()
    instance2 = settings_manager()
    assert instance1 == instance2

# После успешного вызова load() и convert() флаг is_loaded становится True.
def test_true_settings_manager_is_loaded():
   
    manager = settings_manager()
    try:
        manager.load()
    except Exception:
        assert False

    assert manager.is_loaded == True

# Проверяет, что str() и оператор is подтверждают единственность экземпляра.
def test_same_strings_settings_manager_create():
   
    instance1 = settings_manager()
    instance2 = settings_manager()
    try:
        assert str(instance1) == str(instance2)
        assert instance1 is instance2
    except Exception:
        assert False

# После load() метод convert() успешно маппит JSON в settings_model
def test_true_settings_manager_convert():
    
    manager = settings_manager()
    manager.load()
    assert manager.convert() == True


# Проверяет маппинг полей organization из JSON
def test_success_settings_manager_convert_organization_fields():
   
    manager = settings_manager()
    manager.load()

    org = manager.settings.organization
    assert isinstance(org, organization_model)
    assert org.name == "Ромашка"
    assert org.inn == "4444444444"
    assert org.bik == "012345678"
    assert org.account == "12345678901234567890"
    assert org.ownership_form == "ООО"


# Проверяет маппинг строковых полей boss_name и account_name из JSON
def test_success_settings_manager_convert_boss_and_accountant():
   
    manager = settings_manager()
    manager.load()

    assert manager.settings.boss_name == "Иванов Иван Иванович"
    assert manager.settings.account_name == "Петрова Анна Сергеевна"

# Проверяет корректный маппинг булевого флага первого старта
def test_true_settings_manager_is_first_start():
    
    manager = settings_manager()
    manager.load()

    assert manager.settings.is_first_start == True

# Проверяет что при повторном создании объекта возвращается тот же самый экземпляр, а не новый.
def test_same_settings_manager_singleton_identity():
    
    m1 = settings_manager()
    m1.load()

    m2 = settings_manager()
    assert m1.settings is m2.settings
    assert m1.settings.organization == m2.settings.organization