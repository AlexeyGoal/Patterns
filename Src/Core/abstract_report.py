from abc import ABC, abstractmethod
from Src.Dtos.report_result_dto import report_result_dto


"""
Абстрактный класс для формирования отчета
"""
class abstract_report(ABC):
    """
    Базовый абстрактный класс стратегии/компонента формирования отчета.
    """

    @abstractmethod
    def build(self, source) -> report_result_dto:
        """
        Сформировать отчет по переданному источнику данных.
        :param source: Доменная модель-источник данных для отчета
        :return: Экземпляр report_result_dto с результатом
        """
        pass


AbstractReport = abstract_report