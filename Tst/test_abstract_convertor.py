import pytest
from Src.Core.abstract_convertor import abstract_convertor, AbstractConvertor


"""Простой объект-источник для проверки конвертера"""
class sample_object:
    def __init__(self):
        self.code = "001"
        self.name = "Мука"
        self.count = 200


"""Тестовый конвертер, реализующий абстрактный метод Convert"""
class sample_convertor(abstract_convertor):
    def Convert(self, source: object) -> dict:
        return {
            "Код": getattr(source, "code", None),
            "Наименование": getattr(source, "name", None),
            "Количество": getattr(source, "count", None),
        }


"""Тест: абстрактный класс нельзя создать напрямую"""
def test_abstract_convertor_not_instantiable():
    with pytest.raises(TypeError):
        abstract_convertor()


"""Тест: наследник, реализующий Convert, создается и работает"""
def test_convert_returns_dict():
    convertor = sample_convertor()

    result = convertor.Convert(sample_object())

    assert isinstance(result, dict)


"""Тест: ключ - наименование поля, значение - данные поля"""
def test_convert_keys_and_values():
    convertor = sample_convertor()

    result = convertor.Convert(sample_object())

    assert result["Код"] == "001"
    assert result["Наименование"] == "Мука"
    assert result["Количество"] == 200


"""Тест: метод принимает любой объект (в том числе нестандартный)"""
def test_convert_accepts_any_object():
    convertor = sample_convertor()

    assert convertor.Convert(None) == {"Код": None, "Наименование": None, "Количество": None}
    assert convertor.Convert({"name": "Вода"}) == {"Код": None, "Наименование": None, "Количество": None}


"""Тест: без реализации Convert класс остается абстрактным"""
def test_child_without_convert_not_instantiable():
    class incomplete_convertor(abstract_convertor):
        pass

    with pytest.raises(TypeError):
        incomplete_convertor()


"""Тест: алиас AbstractConvertor указывает на тот же класс"""
def test_alias():
    assert AbstractConvertor is abstract_convertor
