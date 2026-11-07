import datetime
import uuid

import pytest

from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.entity import entity
from Src.Logics.convert_service import convert_service, ConvertService
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.recipe_item_model import recipe_item_model
from Src.Models.recipe_model import recipe_model


# Тестовая сущность с полем даты/времени
class event_entity(entity):

    def __init__(self, title: str, moment: datetime.datetime):
        super().__init__()
        self.name = title
        self.__title = title
        self.__moment = moment

    @property
    def title(self):
        return self.__title

    @property
    def moment(self):
        return self.__moment


# Конвертер-заглушка: поддерживает всё и отдаёт заданные поля
class stub_convertor(abstract_convertor):

    def __init__(self, fields: dict):
        self.__fields = fields

    @staticmethod
    def is_supported(source: object) -> bool:
        return True

    def convert(self, source: object) -> dict:
        return dict(self.__fields)


# Фабрика-заглушка: возвращает переданные конверторы и считает вызовы
class stub_factory:

    def __init__(self, convertors: list[abstract_convertor]):
        self.__convertors = convertors
        self.calls = 0

    def resolve(self, source: object) -> list[abstract_convertor]:
        self.calls += 1
        return list(self.__convertors)


# Фикстура: оркестратор конвертации
@pytest.fixture
def service():
    return convert_service()




"""Тест: простое значение превращается в словарь «тип → значение»"""
@pytest.mark.parametrize("value,expected", [
    ("текст", {"str": "текст"}),
    (42, {"int": 42}),
    (3.14, {"float": 3.14}),
])
def test_convert_basic_value(service, value, expected):
    assert service.convert(value) == expected


"""Тест: дата/время превращается в словарь через datetime_convertor"""
def test_convert_datetime(service):
    moment = datetime.datetime(2026, 10, 24, 12, 30)

    assert service.convert(moment) == {"datetime": moment}




"""Тест: список справочников превращается в список их словарей"""
def test_convert_list_of_references_returns_dicts(service):
    gram = range_model("грамм", 1)
    kilogram = range_model("килограмм", 1000, gram)

    result = service.convert([gram, kilogram])

    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["name"] == "грамм"
    assert result[0]["base_range"] is None
    assert result[1]["base_range"]["id"] == gram.id


"""Тест: вложенные ссылки попадают в словарь в виде вложенных словарей, простые поля сохраняются"""
def test_convert_reference_nested_references_as_dicts(service):
    flour = nomenclature_model.create_flour()

    result = service.convert(flour)

    assert result["group"] == {"id": flour.group.id, "name": flour.group.name}
    assert result["range"]["id"] == flour.range.id
    assert result["id"] == flour.id
    assert result["name"] == "Мука пшеничная"
    assert result["full_name"] == "Мука пшеничная высший сорт"


"""Тест: простые поля сущности (в том числе дата/время) сохраняются как есть"""
def test_convert_reference_keeps_simple_fields(service):
    moment = datetime.datetime(2026, 10, 24, 12, 30)
    event = event_entity("Отгрузка", moment)

    result = service.convert(event)

    assert result["title"] == "Отгрузка"
    assert result["moment"] == moment
    assert result["name"] == "Отгрузка"
    assert result["id"] == event.id


"""Тест: списки свойств сущности вкладываются рекурсивно в виде словарей"""
def test_convert_reference_embeds_list_properties(service):
    gram = range_model("грамм", 1)
    recipe = recipe_model.create("Тестовый рецепт", "Описание")
    recipe.add_item(recipe_item_model.create_ingredient("Мука", 200, gram))

    result = service.convert(recipe)

    assert result["name"] == "Тестовый рецепт"
    assert result["packaging"] is None
    assert isinstance(result["items"], list)
    assert result["items"][0]["name"] == "Мука"
    assert result["items"][0]["range"]["id"] == gram.id


"""Тест: позиция рецепта выгружается со всеми полями и ссылкой на единицу измерения"""
def test_convert_recipe_item_reference(service):
    gram = range_model("грамм", 1)
    item = recipe_item_model.create_ingredient("Мука", 200, gram)

    result = service.convert(item)

    assert result["name"] == "Мука"
    assert result["weight"] == 200.0
    assert result["range"]["id"] == gram.id
    assert result["items"] == []




"""Тест: словарь обходится рекурсивно - каждое значение превращается в словарь"""
def test_convert_dict_recursively(service):
    result = service.convert({"count": 42, "title": "Мука"})

    assert result == {"count": {"int": 42}, "title": {"str": "Мука"}}



"""Тест: пустые коллекции остаются пустыми"""
def test_convert_empty_collections(service):
    assert service.convert({}) == {}
    assert service.convert([]) == []


"""Тест: типы вне поддержки конвертеров дают пустой словарь без исключений"""
@pytest.mark.parametrize("value", [None, True, uuid.uuid4(), object()])
def test_convert_unsupported_types_return_empty_dict(service, value):
    assert service.convert(value) == {}


"""Тест: оркестратор принимает любой объект любого типа без исключений"""
@pytest.mark.parametrize("value", [
    None, True, 42, 3.14, "текст", [1, 2], {"a": 1}, uuid.uuid4(), object(),
    datetime.datetime(2026, 10, 24, 12, 30),
    range_model.create_gram(),
])
def test_convert_accepts_any_object(service, value):
    result = service.convert(value)

    assert isinstance(result, (dict, list))




"""Тест: результаты всех подходящих конвертеров мержатся в один словарь"""
def test_convert_merges_convertor_results():
    service = convert_service(stub_factory([
        stub_convertor({"first": 1}),
        stub_convertor({"second": 2}),
    ]))

    assert service.convert("value") == {"first": 1, "second": 2}


"""Тест: при совпадении полей побеждает конвертер, стоящий позже"""
def test_convert_merge_last_convertor_wins():
    service = convert_service(stub_factory([
        stub_convertor({"field": 1}),
        stub_convertor({"field": 2}),
    ]))

    assert service.convert("value") == {"field": 2}


"""Тест: если подходящих конвертеров нет - пустой словарь"""
def test_convert_without_convertors_returns_empty_dict():
    service = convert_service(stub_factory([]))

    assert service.convert("value") == {}


"""Тест: фабрика запрашивается для каждого значения, списки и словари обходятся структурно"""
def test_convert_resolves_convertor_for_every_node():
    factory = stub_factory([stub_convertor({"node": True})])
    service = convert_service(factory)

    result = service.convert({"a": [1, 2]})

    # список и словарь обойдены без фабрики, конвертор запросился для 1 и 2
    assert factory.calls == 2
    assert result == {"a": [{"node": True}, {"node": True}]}


"""Тест: без переданной фабрики оркестратор создаёт свою"""
def test_convert_without_factory_uses_default():
    service = convert_service()

    assert service.convert(42) == {"int": 42}


"""Тест: алиас ConvertService указывает на тот же класс"""
def test_alias():
    assert ConvertService is convert_service
