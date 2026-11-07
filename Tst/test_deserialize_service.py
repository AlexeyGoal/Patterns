import pytest

from Src.Core.abstract_deserializer import abstract_deserializer
from Src.Core.exception import arguments_exception
from Src.Logics.deserialize_service import deserialize_service, DeserializeService
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.recipe_item_model import recipe_item_model, recipe_item_type
from Src.Models.recipe_model import recipe_model


# Фикстура: оркестратор десериализации
@pytest.fixture
def service():
    return deserialize_service()


# Десериализатор-заглушка: поддерживает только словари с ключом stub
class stub_deserializer(abstract_deserializer):

    def __init__(self):
        self.bound_service = None

    @staticmethod
    def is_supported(data: object) -> bool:
        return isinstance(data, dict) and "stub" in data

    def bind(self, service):
        self.bound_service = service
        return self

    def deserialize(self, data: object):
        return {"stub": self.bound_service.deserialize(data.get("stub"))}


# Фабрика-заглушка: возвращает десериализатор-заглушку и считает вызовы
class stub_factory:

    def __init__(self):
        self.calls = 0

    def resolve(self, source: object) -> list[abstract_deserializer]:
        self.calls += 1

        if stub_deserializer.is_supported(source):
            return [stub_deserializer()]

        return []


"""Тест: простые значения JSON возвращаются без изменений"""
@pytest.mark.parametrize("value", [None, True, False, 42, 3.14, "текст"])
def test_deserialize_basic_value(service, value):
    assert service.deserialize(value) == value








"""Тест: единица измерения восстанавливается вместе с базовой единицей"""
def test_deserialize_range_with_base_range(service):
    data = {
        "id": "0fd16cdf-c5db-4a3d-8b09-d96bca173ebe",
        "name": "килограмм",
        "conversion_factor": 1000,
        "base_range": {
            "id": "f9bc2309-f8c2-43d4-928d-052977cd0801",
            "name": "грамм",
            "conversion_factor": 1,
            "base_range": None,
        },
    }

    result = service.deserialize(data)

    assert isinstance(result, range_model)
    assert str(result.id) == data["id"]
    assert result.name == "килограмм"
    assert result.conversion_factor == 1000
    assert isinstance(result.base_range, range_model)
    assert result.base_range.name == "грамм"
    assert result.base_range.base_range is None


"""Тест: номенклатура восстанавливается вместе с группой и единицей измерения"""
def test_deserialize_nomenclature_with_references(service):
    data = {
        "name": "Мука пшеничная",
        "full_name": "Мука пшеничная высший сорт",
        "group": {"name": "Бакалея"},
        "range": {"name": "килограмм", "conversion_factor": 1000, "base_range": None},
    }

    result = service.deserialize(data)

    assert isinstance(result, nomenclature_model)
    assert result.group.name == "Бакалея"
    assert result.range.name == "килограмм"


"""Тест: позиция рецепта восстанавливается с вложенными позициями"""
def test_deserialize_recipe_item_recursively(service):
    data = {
        "name": "Лапша домашняя (полуфабрикат)",
        "weight": 0.0,
        "type": recipe_item_type.SEMI_FINISHED,
        "range": {"name": "грамм", "conversion_factor": 1, "base_range": None},
        "items": [
            {
                "name": "Мука пшеничная",
                "weight": 200,
                "type": recipe_item_type.INGREDIENT,
                "range": {"name": "грамм", "conversion_factor": 1, "base_range": None},
                "items": [],
            }
        ],
    }

    result = service.deserialize(data)

    assert isinstance(result, recipe_item_model)
    assert result.type == recipe_item_type.SEMI_FINISHED
    assert len(result.items) == 1
    assert result.items[0].name == "Мука пшеничная"
    assert result.items[0].weight == 200.0


"""Тест: рецепт восстанавливается с позициями и вложенными рецептами"""
def test_deserialize_recipe_with_sub_recipes(service):
    data = {
        "name": "Суп-лапша домашняя",
        "description": "Традиционный суп",
        "items": [
            {
                "name": "Курица (тушка)",
                "weight": 900,
                "type": recipe_item_type.INGREDIENT,
                "range": {"name": "грамм", "conversion_factor": 1, "base_range": None},
                "items": [],
            }
        ],
        "sub_recipes": [
            {
                "name": "Бульон куриный",
                "description": "Основа супа",
                "items": [],
                "sub_recipes": [],
            }
        ],
    }

    result = service.deserialize(data)

    assert isinstance(result, recipe_model)
    assert len(result.items) == 1
    assert len(result.sub_recipes) == 1
    assert result.sub_recipes[0].name == "Бульон куриный"
    assert result.is_composite is True


"""Тест: некорректный идентификатор приводит к arguments_exception"""
def test_deserialize_invalid_id_raises_exception(service):
    data = {"id": "not-a-uuid", "name": "грамм", "conversion_factor": 1, "base_range": None}

    with pytest.raises(arguments_exception):
        service.deserialize(data)


"""Тест: не-словарь передаётся в конкретный десериализатор только фабрикой"""
def test_deserialize_without_suitable_deserializer_returns_structure():
    factory = stub_factory()
    service_instance = deserialize_service(factory)

    result = service_instance.deserialize({"items": [1, 2]})

    assert result == {"items": [1, 2]}


"""Тест: оркестратор привязывает себя к десериализатору для рекурсивных вызовов"""
def test_deserialize_binds_service_to_deserializer():
    factory = stub_factory()
    service_instance = deserialize_service(factory)

    result = service_instance.deserialize({"stub": [1, 2]})

    assert result == {"stub": [1, 2]}


"""Тест: фабрика запрашивается для каждого словаря"""
def test_deserialize_resolves_factory_for_every_dict():
    factory = stub_factory()
    service_instance = deserialize_service(factory)

    service_instance.deserialize([{"unknown": 1}, {"unknown": 2}])

    assert factory.calls == 2


"""Тест: без переданной фабрики оркестратор создаёт свою"""
def test_deserialize_without_factory_uses_default(service):
    result = service.deserialize({"name": "Овощи"})

    assert isinstance(result, nomenclature_group_model)


"""Тест: алиас DeserializeService указывает на тот же класс"""
def test_alias():
    assert DeserializeService is deserialize_service
