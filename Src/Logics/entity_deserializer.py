import uuid

from Src.Core.abstract_deserializer import abstract_deserializer
from Src.Core.entity import entity
from Src.Core.exception import arguments_exception


"""
Базовый десериализатор сущностей.

Восстанавливает общие поля (id, name) и предоставляет наследникам
рекурсивный обход вложенных значений через deserialize_service.
"""
class entity_deserializer(abstract_deserializer):

    """Сервис рекурсивной десериализации, привязывается оркестратором"""
    __service = None


    """Привязать оркестратор десериализации для рекурсивных вызовов"""
    def bind(self, service):
        self.__service = service
        return self


    """Оркестратор десериализации: создаётся по требованию при прямом вызове"""
    @property
    def service(self):
        if self.__service is None:
            from Src.Logics.deserialize_service import deserialize_service
            self.__service = deserialize_service()
        return self.__service


    """Проверить, что данные похожи на словарь сущности"""
    @staticmethod
    def is_supported(data: object) -> bool:
        return isinstance(data, dict) and "name" in data


    """Создать модель по словарю полей (переопределяется наследниками)"""
    def create_model(self, data: dict) -> entity:
        raise NotImplementedError(f"{type(self).__name__} must implement create_model")


    """Десериализовать словарь в модель и восстановить идентификатор"""
    def deserialize(self, data: object) -> entity:
        if not isinstance(data, dict):
            raise arguments_exception("data", f"{type(self).__name__} supports only dict type")

        model = self.create_model(data)

        if not isinstance(model, entity):
            raise arguments_exception("data", "deserializer must create an entity")

        identifier = data.get("id")
        if identifier is not None:
            try:
                model.id = uuid.UUID(str(identifier))
            except (ValueError, TypeError, AttributeError) as error:
                raise arguments_exception("id", f"id must be a valid UUID: {error}") from error

        return model


    """Рекурсивно десериализовать вложенное значение через оркестратор"""
    def _deserialize_value(self, value):
        if isinstance(value, (dict, list)):
            return self.service.deserialize(value)
        return value


    """Прочитать обязательное поле словаря"""
    @staticmethod
    def _require(data: dict, field: str):
        if field not in data:
            raise arguments_exception(field, f"field '{field}' is required")
        return data.get(field)


EntityDeserializer = entity_deserializer
