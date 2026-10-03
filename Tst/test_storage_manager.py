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

    liter = next(r for r in manager.ranges.values() if r.name == "литр")
    assert liter.conversion_factor == 1000
    assert liter.base_range is not None
    assert liter.base_range.name == "миллилитр"

    
    gram = next(r for r in manager.ranges.values() if r.name == "грамм")
    assert gram.base_range is None

    ml = next(r for r in manager.ranges.values() if r.name == "миллилитр")
    assert ml.base_range is None


#Проверяет наличие групп Мясные продукты, Овощи, Молочные продукты, Бакалея, Полуфабрикаты и Блюда.
def test_success_storage_manager_first_start_groups():
    
    manager = storage_manager()
    manager.convert()

    assert len(manager.groups) == 6
    group_names = [g.name for g in manager.groups.values()]
    assert "Мясные продукты" in group_names
    assert "Овощи" in group_names
    assert "Молочные продукты" in group_names
    assert "Бакалея" in group_names
    assert "Полуфабрикаты" in group_names
    assert "Блюда" in group_names

# Проверяет корректные связи номенклатуры с группами и единицами.
def test_success_storage_manager_first_start_nomenclatures():

    # Подготовка
    manager = storage_manager()

    # Действие
    manager.convert()

    # Проверки
    assert len(manager.nomenclatures) == 12
    nom_names = [n.name for n in manager.nomenclatures.values()]
    assert "Курица (тушка)" in nom_names
    assert "Морковь" in nom_names
    assert "Лук репчатый" in nom_names
    assert "Картофель" in nom_names
    assert "Лапша домашняя (полуфабрикат)" in nom_names
    assert "Сметана 15%" in nom_names
    assert "Суп-лапша домашняя" in nom_names

    # Проверяем связи ингредиента из группы «Мясные продукты»
    chicken = next(n for n in manager.nomenclatures.values() if n.name == "Курица (тушка)")
    assert chicken.group.name == "Мясные продукты"
    assert chicken.range.name == "килограмм"

    # Проверяем связи ингредиента из группы «Овощи»
    carrot = next(n for n in manager.nomenclatures.values() if n.name == "Морковь")
    assert carrot.group.name == "Овощи"
    assert carrot.range.name == "килограмм"

    # Проверяем связи полуфабриката
    noodles = next(n for n in manager.nomenclatures.values() if n.name == "Лапша домашняя (полуфабрикат)")
    assert noodles.group.name == "Полуфабрикаты"
    assert noodles.range.name == "килограмм"

    # Проверяем связи ингредиента из группы «Бакалея» в штуках
    bay_leaf = next(n for n in manager.nomenclatures.values() if n.name == "Лавровый лист")
    assert bay_leaf.group.name == "Бакалея"
    assert bay_leaf.range.name == "штука"

    # Проверяем связи готового блюда
    soup = next(n for n in manager.nomenclatures.values() if n.name == "Суп-лапша домашняя")
    assert soup.group.name == "Блюда"
    assert soup.range.name == "штука"



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




# Проверка поведения при is_first_start == False
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