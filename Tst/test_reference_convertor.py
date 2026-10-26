import pytest
from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.entity import entity
from Src.Core.exception import arguments_exception
from Src.Logics.reference_convertor import reference_convertor, ReferenceConvertor
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.recipe_item_model import recipe_item_model
from Src.Models.recipe_model import recipe_model


"""Тест: reference_convertor является наследником abstract_convertor"""
def test_reference_convertor_is_abstract_convertor():
    convertor = reference_convertor()

    assert isinstance(convertor, abstract_convertor)


"""Тест: в словарь попадают все публичные поля, вложенные ссылки - в виде словарей"""
def test_convert_reference_returns_all_public_fields():
    convertor = reference_convertor()
    flour = nomenclature_model.create_flour()

    result = convertor.convert(flour)

    assert set(result.keys()) == {"id", "name", "full_name", "group", "range"}
    assert result["id"] == flour.id
    assert result["name"] == "Мука пшеничная"
    assert result["full_name"] == "Мука пшеничная высший сорт"
    assert result["group"] == {"id": flour.group.id, "name": flour.group.name}
    assert result["range"]["id"] == flour.range.id


"""Тест: простые свойства (id, name, conversion_factor) тоже попадают в словарь"""
def test_convert_reference_includes_simple_properties():
    convertor = reference_convertor()
    unit = range_model.create_gram("грамм")

    result = convertor.convert(unit)

    assert result["name"] == "грамм"
    assert result["conversion_factor"] == 1
    assert result["base_range"] is None


"""Тест: свойство со значением None выгружается в виде null"""
def test_convert_reference_none_value_exported_as_null():
    class value_entity(entity):

        @property
        def value(self):
            return None

    convertor = reference_convertor()

    result = convertor.convert(value_entity())

    assert result["value"] is None
    assert set(result.keys()) == {"id", "name", "value"}


"""Тест: вложенный справочник раскрывается в словарь своих полей"""
def test_convert_reference_expands_nested_reference():
    convertor = reference_convertor()
    unit = range_model.create_kilogram("килограмм", "грамм")

    result = convertor.convert(unit)

    assert result["base_range"] == {
        "id": unit.base_range.id,
        "name": "грамм",
        "conversion_factor": 1,
        "base_range": None,
    }
    assert not isinstance(result["base_range"], range_model)


"""Тест: ссылки на другие сущности раскрываются в словари, собственный id сохраняется"""
def test_convert_reference_expands_references_into_dicts():
    convertor = reference_convertor()
    flour = nomenclature_model.create_flour()

    result = convertor.convert(flour)

    assert result["group"]["id"] == flour.group.id
    assert result["range"]["id"] == flour.range.id
    assert result["id"] == flour.id


"""Тест: вложенный объект раскрывается до словаря простых полей """
def test_convert_reference_expands_nested_object():
    class author_entity(entity):
        pass

    class book_entity(entity):

        def __init__(self, author):
            super().__init__()  
            self.name = "Книга"
            self.__author = author

        @property
        def author(self):
            return self.__author

    author = author_entity()
    author.name = "Иван"
    convertor = reference_convertor()

    result = convertor.convert(book_entity(author))

    assert result["author"] == {"id": author.id, "name": "Иван"}


"""Тест: вложенность раскрывается на всю глубину - ссылка на ссылку на ссылку"""
def test_convert_reference_expands_nested_objects_recursively():
    gram = range_model.create_gram()
    kilogram = range_model("килограмм", 1000, gram)
    recipe = recipe_model.create("Тестовый рецепт", "Описание")
    recipe.add_item(recipe_item_model.create_ingredient("Мука", 200, kilogram))

    convertor = reference_convertor()

    result = convertor.convert(recipe)

    assert result["items"][0]["range"]["base_range"]["id"] == gram.id
    assert result["items"][0]["range"]["base_range"]["name"] == "грамм"


"""Тест: списки раскрываются в списки словарей"""
def test_convert_reference_expands_lists():
    gram = range_model.create_gram()
    recipe = recipe_model.create("Тестовый рецепт", "Описание")
    recipe.add_item(recipe_item_model.create_ingredient("Мука", 200, gram))

    convertor = reference_convertor()

    result = convertor.convert(recipe)

    assert isinstance(result["items"], list)
    assert result["items"][0]["name"] == "Мука"
    assert result["items"][0]["range"]["id"] == gram.id


"""Тест: циклическая ссылка раскрывается до id, а не приводит к бесконечной рекурсии"""
def test_convert_reference_cycle_falls_back_to_id():
    class node_entity(entity):

        @property
        def parent(self):
            return self.__parent

        @parent.setter
        def parent(self, value):
            self.__parent = value

    first = node_entity()
    second = node_entity()
    first.parent = second
    second.parent = first

    convertor = reference_convertor()

    result = convertor.convert(first)

    assert result["parent"]["id"] == second.id
    assert result["parent"]["parent"] == first.id


"""Тест: приватные поля и методы не попадают в словарь"""
def test_convert_reference_skips_private_and_methods():
    convertor = reference_convertor()
    flour = nomenclature_model.create_flour()

    result = convertor.convert(flour)

    for key in result:
        assert not key.startswith("_")
        assert not callable(result[key])


"""Тест: простые типы не поддерживаются и вызывают исключение"""
@pytest.mark.parametrize("source", [42, 3.14, "Бакалея", None, [1], {"name": "x"}, object()])
def test_convert_unsupported_types_raises_exception(source):
    convertor = reference_convertor()

    with pytest.raises(arguments_exception):
        convertor.convert(source)


"""Тест: is_supported возвращает True для наследников entity"""
def test_is_supported_reference():
    assert reference_convertor.is_supported(nomenclature_group_model("Бакалея")) is True
    assert reference_convertor.is_supported(range_model.create_gram()) is True


"""Тест: is_supported возвращает False для не-справочников"""
def test_is_supported_unsupported_types():
    assert reference_convertor.is_supported(42) is False
    assert reference_convertor.is_supported("text") is False
    assert reference_convertor.is_supported(None) is False


"""Тест: ошибка чтения свойства преобразуется в arguments_exception"""
def test_convert_reference_broken_property_raises_exception():
    class broken_entity(entity):
        @property
        def boom(self):
            raise ValueError("broken property")

    convertor = reference_convertor()

    with pytest.raises(arguments_exception):
        convertor.convert(broken_entity())


"""Тест: алиас ReferenceConvertor указывает на тот же класс"""
def test_alias():
    assert ReferenceConvertor is reference_convertor
