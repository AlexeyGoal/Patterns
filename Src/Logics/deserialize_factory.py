from Src.Core.abstract_deserializer import AbstractDeserializer
from Src.Logics.settings_deserializer import settings_deserializer
from Src.Logics.organization_deserializer import organization_deserializer
from Src.Logics.storage_deserializer import storage_deserializer
from Src.Logics.range_deserializer import range_deserializer
from Src.Logics.nomenclature_deserializer import nomenclature_deserializer
from Src.Logics.recipe_deserializer import recipe_deserializer
from Src.Logics.recipe_item_deserializer import recipe_item_deserializer
from Src.Logics.nomenclature_group_deserializer import nomenclature_group_deserializer


"""
Фабрика десериализаторов
"""
class deserialize_factory:
    """Фабрика десериализаторов: подбирает десериализатор под словарь полей"""


    """Зарегистрированные классы десериализаторов (от частного к общему)"""
    __deserializer_types: list[type[AbstractDeserializer]]


    """Конструктор: регистрирует десериализаторы моделей приложения"""
    def __init__(self):

        self.__deserializer_types = [
            settings_deserializer,
            organization_deserializer,
            storage_deserializer,
            range_deserializer,
            nomenclature_deserializer,
            recipe_deserializer,
            recipe_item_deserializer,
            nomenclature_group_deserializer,
        ]


    """
    Возвращает список созданных десериализаторов, поддерживающих словарь.
    """
    def resolve(self, source: object) -> list[AbstractDeserializer]:

        if not isinstance(source, dict):
            return []

        return [
            deserializer_type()
            for deserializer_type in self.__deserializer_types
            if deserializer_type.is_supported(source)
        ]


DeserializeFactory = deserialize_factory
