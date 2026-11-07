import pytest
from Src.Core.abstract_deserializer import abstract_deserializer, AbstractDeserializer


"""Тестовые данные для проверки контракта десериализатора"""
class sample_entity:
    def __init__(self, name="Мука"):
        self.name = name


"""Тестовый десериализатор, реализующий абстрактные методы фабричного контракта"""
class sample_deserializer(abstract_deserializer):

    @staticmethod
    def is_supported(data: object) -> bool:
        return isinstance(data, dict) and "name" in data

    def deserialize(self, data: object) -> object:
        return sample_entity(data.get("name", ""))





"""Тест: наследник, реализующий deserialize, создаётся и работает"""
def test_deserialize_returns_object():
    deserializer = sample_deserializer()

    result = deserializer.deserialize({"name": "Сахар"})

    assert isinstance(result, sample_entity)
    assert result.name == "Сахар"


"""Тест: is_supported вызывается и через класс, и через инстанс"""
def test_is_supported_contract():
    assert sample_deserializer.is_supported({"name": "Мука"}) is True
    assert sample_deserializer().is_supported({"name": "Мука"}) is True


"""Тест: без реализации deserialize класс остаётся абстрактным"""
def test_child_without_deserialize_not_instantiable():
    class incomplete_deserializer(abstract_deserializer):
        @staticmethod
        def is_supported(data: object) -> bool:
            return True

    with pytest.raises(TypeError):
        incomplete_deserializer()


"""Тест: без реализации is_supported класс остаётся абстрактным (часть контракта фабрики)"""
def test_child_without_is_supported_not_instantiable():
    class incomplete_deserializer(abstract_deserializer):
        def deserialize(self, data: object) -> object:
            return data

    with pytest.raises(TypeError):
        incomplete_deserializer()



