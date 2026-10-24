from Src.Core.abstract_convertor import abstract_convertor, AbstractConvertor
from Src.Core.entity import entity
from Src.Core.exception import arguments_exception


"""
Конвертор ссылок
"""
class reference_convertor(abstract_convertor):
    

    @staticmethod
    def is_supported(source: object) -> bool:

        return isinstance(source, entity)


    """
    Конвертировать справочник в словарь полей.
    Свойства-ссылки на другие сущности заменяются их id.
    """
    def Convert(self, source: object) -> dict:

        if not self.is_supported(source):
            raise arguments_exception("source", "reference_convertor supports only Reference type (entity child)")

        result = {}

        for name in dir(type(source)):

            if name.startswith("_"):
                continue

            if not isinstance(getattr(type(source), name, None), property):
                continue

            try:
                value = getattr(source, name)
            except Exception as error:
                raise arguments_exception("source", f"property '{name}' cannot be read: {error}")


            result[name] = value.id if isinstance(value, entity) else value

        return result


ReferenceConvertor = reference_convertor
