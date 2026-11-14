import json

from Src.Core.validator import operation_exception
from Src.Logics.deserialize_service import deserialize_service, DeserializeService


"""
Загрузка JSON-файлов и восстановление доменных моделей
"""
class json_deserializer:

    """Оркестратор десериализации"""
    __service: deserialize_service


    """Конструктор: использует переданный сервис или создаёт свой"""
    def __init__(self, service: deserialize_service = None):

        self.__service = service if service is not None else deserialize_service()


    """Загрузить JSON-файл и восстановить из него модели"""
    def load(self, file_name: str):

        try:
            with open(file_name, "r", encoding="utf-8") as file:
                data = json.load(file)

        except Exception as error:
            raise operation_exception(
                f"Ошибка при загрузке данных из файла {file_name}: {error}"
            ) from error

        return self.deserialize(data)


    """Восстановить модели из строки JSON"""
    def loads(self, text: str):

        try:
            data = json.loads(text)

        except Exception as error:
            raise operation_exception(f"Ошибка при разборе JSON: {error}") from error

        return self.deserialize(data)


    """Восстановить модели из уже разобранных данных JSON"""
    def deserialize(self, data: object):

        return self.__service.deserialize(data)


JsonDeserializer = json_deserializer
