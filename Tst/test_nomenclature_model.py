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



"""Тест выброса argument_exception при передаче строки вместо объекта единицы 测量."""
def test_argument_exception_nomenclature_model_invalid_range_type():

    group = nomenclature_group_model("Мясо")

    with pytest.raises(arguments_exception):
        nomenclature_model("Говядина", "Говядина полное", group, "грамм")


"""Тест фабричного метода create_flour"""
def test_success_nomenclature_model_create_flour():

    item = nomenclature_model.create_flour()

    assert item.name == "Мука пшеничная"
    assert item.full_name == "Мука пшеничная высший сорт"
    assert item.group.name == "Бакалея"
    assert item.range.name == "килограмм"


"""Тест фабричного метода create_milk"""
def test_success_nomenclature_model_create_milk():

    item = nomenclature_model.create_milk()

    assert item.name == "Молоко 3.2%"
    assert item.full_name == "Молоко коровье пастеризованное 3.2%"
    assert item.group.name == "Молочные продукты"
    assert item.range.name == "литр"


"""Тест фабричного метода create_eggs"""
def test_success_nomenclature_model_create_eggs():

    item = nomenclature_model.create_eggs()

    assert item.name == "Яйца куриные"
    assert item.full_name == "Яйца куриные столовые С0"
    assert item.group.name == "Молочные продукты"
    assert item.range.name == "штука"


"""Тест фабричного метода create_butter"""
def test_success_nomenclature_model_create_butter():

    item = nomenclature_model.create_butter()

    assert item.name == "Масло сливочное"
    assert item.full_name == "Масло сливочное крестьянское 72.5%"
    assert item.group.name == "Молочные продукты"
    assert item.range.name == "килограмм"


"""Тест фабричного метода create_sugar"""
def test_success_nomenclature_model_create_sugar():

    item = nomenclature_model.create_sugar()

    assert item.name == "Сахар"
    assert item.full_name == "Сахар белый кристаллический"
    assert item.group.name == "Бакалея"
    assert item.range.name == "килограмм"


"""Тест фабричного метода create_salt"""
def test_success_nomenclature_model_create_salt():

    item = nomenclature_model.create_salt()

    assert item.name == "Соль"
    assert item.full_name == "Соль поваренная пищевая"
    assert item.group.name == "Бакалея"
    assert item.range.name == "килограмм"


"""Тест фабричного метода create_cottage_cheese"""
def test_success_nomenclature_model_create_cottage_cheese():

    item = nomenclature_model.create_cottage_cheese()

    assert item.name == "Творог 9%"
    assert item.full_name == "Творог 9% протёртый"
    assert item.group.name == "Молочные продукты"
    assert item.range.name == "килограмм"


"""Тест фабричного метода create_sunflower_oil"""
def test_success_nomenclature_model_create_sunflower_oil():

    item = nomenclature_model.create_sunflower_oil()

    assert item.name == "Масло подсолнечное"
    assert item.full_name == "Масло подсолнечное рафинированное"
    assert item.group.name == "Бакалея"
    assert item.range.name == "литр"


"""Тест фабричного метода create_breakfast_box"""
def test_success_nomenclature_model_create_breakfast_box():

    item = nomenclature_model.create_breakfast_box()

    assert item.name == "Коробка для завтраков"
    assert item.full_name == "Коробка бумажная для завтраков"
    assert item.group.name == "Упаковка"
    assert item.range.name == "штука"


"""Тест фабричного метода create_dish_noodle_soup"""
def test_success_nomenclature_model_create_dish_noodle_soup():

    item = nomenclature_model.create_dish_noodle_soup()

    assert item.name == "Суп-лапша домашняя"
    assert item.full_name == "Суп-лапша домашняя в порционной тарелке"
    assert item.group.name == "Блюда"
    assert item.range.name == "штука"


"""Тест фабричного метода create_chicken"""
def test_success_nomenclature_model_create_chicken():

    item = nomenclature_model.create_chicken()

    assert item.name == "Курица (тушка)"
    assert item.full_name == "Курица тушка охлаждённая"
    assert item.group.name == "Мясные продукты"
    assert item.range.name == "килограмм"


"""Тест фабричного метода create_carrot"""
def test_success_nomenclature_model_create_carrot():

    item = nomenclature_model.create_carrot()

    assert item.name == "Морковь"
    assert item.full_name == "Морковь свежая мытая"
    assert item.group.name == "Овощи"
    assert item.range.name == "килограмм"


"""Тест фабричного метода create_onion"""
def test_success_nomenclature_model_create_onion():

    item = nomenclature_model.create_onion()

    assert item.name == "Лук репчатый"
    assert item.full_name == "Лук репчатый свежий"
    assert item.group.name == "Овощи"
    assert item.range.name == "килограмм"


"""Тест фабричного метода create_potato"""
def test_success_nomenclature_model_create_potato():

    item = nomenclature_model.create_potato()

    assert item.name == "Картофель"
    assert item.full_name == "Картофель свежий мытый"
    assert item.group.name == "Овощи"
    assert item.range.name == "килограмм"


"""Тест фабричного метода create_semi_finished_noodles"""
def test_success_nomenclature_model_create_semi_finished_noodles():

    item = nomenclature_model.create_semi_finished_noodles()

    assert item.name == "Лапша домашняя (полуфабрикат)"
    assert item.full_name == "Лапша домашняя полуфабрикат замороженный"
    assert item.group.name == "Полуфабрикаты"
    assert item.range.name == "килограмм"


"""Тест фабричного метода create_sour_cream"""
def test_success_nomenclature_model_create_sour_cream():

    item = nomenclature_model.create_sour_cream()

    assert item.name == "Сметана 15%"
    assert item.full_name == "Сметана 15% пастеризованная"
    assert item.group.name == "Молочные продукты"
    assert item.range.name == "килограмм"


"""Тест фабричного метода create_bay_leaf"""
def test_success_nomenclature_model_create_bay_leaf():

    item = nomenclature_model.create_bay_leaf()

    assert item.name == "Лавровый лист"
    assert item.full_name == "Лавровый лист сухой"
    assert item.group.name == "Бакалея"
    assert item.range.name == "штука"