import pytest
from Src.Logics.storage_manager import storage_manager
from Src.Logics.settings_manager import settings_manager
from Src.Models.storage_model import storage_model
from Src.Models.range_model import range_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.settings_model import settings_model


# Набор модульных тестов для класса storage_manager 


# Проверяет оператор is — оба инстанса ссылаются на один объект.
def test_same_instance_storage_manager_singleton():
   
    m1 = storage_manager()
    m2 = storage_manager()
    assert m1 is m2


# Проверяет равенство двух инстансов синглтона.
def test_equal_storage_manager_singleton():
    
    m1 = storage_manager()
    m2 = storage_manager()
    assert m1 == m2


# Коллекции ranges и nomenclatures ссылаются на одни объекты.
def test_shared_data_storage_manager_singleton():
    
    m1 = storage_manager()
    m1.convert()
    m2 = storage_manager()

    assert m1.ranges is m2.ranges
    assert m1.nomenclatures is m2.nomenclatures
    assert len(m1.ranges) == len(m2.ranges)


# 2. Проверка первого старта и сформированных данных

# Проверяет успешность выполнения метода convert
def test_true_storage_manager_convert():
    
    manager = storage_manager()
    assert manager.convert() == True

# После вызова convert внутренний флаг инициализации становится True.
def test_true_storage_manager_is_initialized():
    
    manager = storage_manager()
    manager.convert()
    assert manager.is_initialized == True


# Проверяет контракт базового класса abstract_manager
def test_true_storage_manager_is_loaded():
   
    manager = storage_manager()
    manager.convert()
    assert manager.is_loaded == True


# Проверяет наличие грамм, килограмм, штука, литр, миллилитр
def test_success_storage_manager_first_start_ranges():
   
    manager = storage_manager()
    manager.convert()

    assert len(manager.ranges) == 5
    names = [r.name for r in manager.ranges.values()]
    assert "грамм" in names
    assert "килограмм" in names
    assert "литр" in names
    assert "миллилитр" in names
    assert "штука" in names

    kg = next(r for r in manager.ranges.values() if r.name == "килограмм")
    assert kg.conversion_factor == 1000
    assert kg.base_range is not None
    assert kg.base_range.name == "грамм"

# Проверяет наличие групп Бакалея, Молочные продукты и Блюда.
def test_success_storage_manager_first_start_groups():
   
    manager = storage_manager()
    manager.convert()

    assert len(manager.groups) == 3
    group_names = [g.name for g in manager.groups.values()]
    assert "Бакалея" in group_names
    assert "Молочные продукты" in group_names
    assert "Блюда" in group_names


# Проверяет корректные связи номенклатуры с группами и единицами
def test_success_storage_manager_first_start_nomenclatures():

    manager = storage_manager()
    manager.convert()

    assert len(manager.nomenclatures) == 7
    nom_names = [n.name for n in manager.nomenclatures.values()]
    assert "Мука пшеничная" in nom_names
    assert "Молоко 3.2%" in nom_names
    assert "Яйца куриные" in nom_names
    assert "Масло сливочное" in nom_names
    assert "Блины классические" in nom_names

    flour = next(n for n in manager.nomenclatures.values() if n.name == "Мука пшеничная")
    assert flour.group.name == "Бакалея"
    assert flour.range.name == "килограмм"

    pancakes = next(n for n in manager.nomenclatures.values() if n.name == "Блины классические")
    assert pancakes.group.name == "Блюда"
    assert pancakes.range.name == "штука"


# Проверяет наличие Основного склада и Холодильника цеха
def test_success_storage_manager_first_start_storages():
    
    manager = storage_manager()
    manager.convert()

    assert len(manager.storages) == 2
    storage_names = [s.name for s in manager.storages.values()]
    assert "Основной склад" in storage_names
    assert "Холодильник цеха" in storage_names


# 3. Проверка уникальности и валидации



def test_false_storage_manager_add_duplicate_range():
    
    manager = storage_manager()
    manager.convert()

    existing_range = list(manager.ranges.values())[0]
    count_before = len(manager.ranges)

    result = manager.add_range(existing_range)
    assert result == False
    assert len(manager.ranges) == count_before


# Добавление нового склада с уникальным id увеличивает размер коллекции
def test_true_storage_manager_add_new_storage():
    
    manager = storage_manager()
    manager.convert()

    count_before = len(manager.storages)
    new_storage = storage_model(name="Архивный склад", address="ул. Складская, 1")

    result = manager.add_storage(new_storage)
    assert result == True
    assert len(manager.storages) == count_before + 1


# Передача строки, числа, None или списка вместо моделей возвращает False
def test_false_storage_manager_add_invalid_type():
    
    manager = storage_manager()
    assert manager.add_storage("не склад") == False
    assert manager.add_range(123) == False
    assert manager.add_nomenclature(None) == False
    assert manager.add_group([]) == False



def test_success_storage_manager_convert_idempotent():
   
    manager = storage_manager()
    manager.convert()

    count_ranges = len(manager.ranges)
    count_noms = len(manager.nomenclatures)

    result = manager.convert()
    assert result == True
    assert len(manager.ranges) == count_ranges
    assert len(manager.nomenclatures) == count_noms


# 4. Проверка поведения при is_first_start == False
def test_empty_storage_manager_convert_is_first_start_false():
    
    if hasattr(storage_manager, 'instance'):
        del storage_manager.instance

    # Создаём настройки с флагом False без чтения диска
    custom_settings = settings_model()
    custom_settings.is_first_start = False

    try:
        manager = storage_manager()
        result = manager.convert(settings=custom_settings)

        assert result == True
        assert len(manager.ranges) == 0
        assert len(manager.groups) == 0
        assert len(manager.nomenclatures) == 0
        assert len(manager.storages) == 0
    finally:
        if hasattr(storage_manager, 'instance'):
            del storage_manager.instance