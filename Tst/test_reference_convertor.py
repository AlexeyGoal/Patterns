import pytest
from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.entity import entity
from Src.Core.exception import arguments_exception
from Src.Logics.reference_convertor import reference_convertor, ReferenceConvertor
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model


"""Тест: reference_convertor является наследником abstract_convertor"""
def test_reference_convertor_is_abstract_convertor():
    convertor = reference_convertor()

    assert isinstance(convertor, abstract_convertor)


"""Тест: справочник конвертируется в словарь с базовыми полями id и name"""
def test_convert_reference_returns_dict_with_id_and_name():
    convertor = reference_convertor()
    group = nomenclature_group_model("Бакалея")

    result = convertor.Convert(group)

    assert isinstance(result, dict)
    assert result["id"] == group.id
    assert result["name"] == "Бакалея"


"""Тест: в словарь попадают собственные свойства модели справочника"""
def test_convert_reference_includes_model_properties():
    convertor = reference_convertor()
    unit = range_model.create_gram("грамм")

    result = convertor.Convert(unit)

    assert result["conversion_factor"] == 1
    assert result["base_range"] is None


"""Тест: вложенный справочник попадает в словарь в виде своего id"""
def test_convert_reference_keeps_nested_reference():
    convertor = reference_convertor()
    unit = range_model.create_kilogram("килограмм", "грамм")

    result = convertor.Convert(unit)

    assert result["base_range"] == unit.base_range.id
    assert not isinstance(result["base_range"], range_model)


"""Тест: ссылки на другие сущности заменяются их id"""
def test_convert_reference_replaces_references_with_ids():
    convertor = reference_convertor()
    flour = nomenclature_model.create_flour()

    result = convertor.Convert(flour)

    assert result["group"] == flour.group.id
    assert result["range"] == flour.range.id
    assert result["id"] == flour.id


"""Тест: приватные поля и методы не попадают в словарь"""
def test_convert_reference_skips_private_and_methods():
    convertor = reference_convertor()
    group = nomenclature_group_model("Бакалея")

    result = convertor.Convert(group)

    for key in result:
        assert not key.startswith("_")
        assert not callable(result[key])


"""Тест: простые типы не поддерживаются и вызывают исключение"""
@pytest.mark.parametrize("source", [42, 3.14, "Бакалея", None, [1], {"name": "x"}, object()])
def test_convert_unsupported_types_raises_exception(source):
    convertor = reference_convertor()

    with pytest.raises(arguments_exception):
        convertor.Convert(source)


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
        convertor.Convert(broken_entity())


"""Тест: алиас ReferenceConvertor указывает на тот же класс"""
def test_alias():
    assert ReferenceConvertor is reference_convertor
