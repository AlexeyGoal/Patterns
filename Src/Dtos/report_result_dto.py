from Src.Core.entity import entity
from Src.Core.validator import validator


class report_result_dto(entity):
    """
    DTO для инкапсуляции результата формирования отчета (текстового или бинарного).
    """
    __text: str = ""
    __binary: list = []

    def __init__(self, text: str = "", binary: list = None):
        """
        Конструктор DTO результата отчета.
        :param text: Текстовое содержимое отчета
        :param binary: Бинарное содержимое отчета (список байт/чисел)
        """
        super().__init__()
        self.__text = text if (binary is None or len(binary) == 0) else ""
        self.__binary = binary if binary is not None else []

    @property
    def text(self) -> str:
        """
        Возвращает текстовый результат отчета.
        """
        return self.__text

    @text.setter
    def text(self, value: str) -> None:
        """
        Устанавливает текстовый результат отчета.
        При установке текста бинарные данные очищаются.
        """
        validator.validate(value, str)
        self.__text = value
        self.__binary = []

    @property
    def binary(self) -> list:
        """
        Возвращает бинарный результат отчета.
        """
        return self.__binary

    @binary.setter
    def binary(self, value: list) -> None:
        """
        Устанавливает бинарный результат отчета.
        При установке непустых бинарных данных текстовое поле очищается.
        """
        if value is not None and len(value) > 0:
            self.__text = ""
            self.__binary = value
        else:
            self.__binary = []


ReportResultDto = report_result_dto