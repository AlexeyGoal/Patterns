from Src.Core.abstract_convertor import abstract_convertor, AbstractConvertor
from Src.Core.exception import arguments_exception


"""
Реализация конвертера для простых типов: numeric и str
"""
class basic_convertor(abstract_convertor):
    """
    Конвертер простых значений в словарь полей.
    """

    __numeric_types = (int, float)


    __string_types = (str,)


    """Проверить, что значение относится к простым типам (numeric или str)"""
    @staticmethod
    def is_supported(source: object) -> bool:

        # bool является подклассом int, но к числовым типам не относится
        if isinstance(source, bool):
            return False

        return isinstance(source, basic_convertor.__numeric_types + basic_convertor.__string_types)


    """
    Конвертировать простое значение в словарь полей.
    """
    def convert(self, source: object) -> dict:

        if not self.is_supported(source):
            raise arguments_exception("source", "basic_convertor supports only numeric and str types")

        return {type(source).__name__: source}


BasicConvertor = basic_convertor
