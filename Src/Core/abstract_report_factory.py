from abc import ABC, abstractmethod
from Src.Core.abstract_report import abstract_report, AbstractReport
from Src.Dtos.report_type_dto import report_type_dto, ReportTypeEnum


"""
Абстрактная фабрика отчетов
"""
class abstract_report_factory(ABC):
    """
    Базовая абстрактная фабрика для создания отчетов по их типу.
    """

    @abstractmethod
    def create(self, report_type: report_type_dto) -> abstract_report:
        """
        Подобрать и создать инстанс нужного отчета по переданному типу.
        :param report_type: Тип требуемого отчета (из report_type_dto)
        :return: Экземпляр конкретного отчета (наследника abstract_report)
        """
        pass

    @abstractmethod
    def create_default(self) -> abstract_report:
        """
        Создать отчет по умолчанию на основе настроек приложения (response_format).
        :return: Экземпляр конкретного отчета (наследника abstract_report)
        """
        pass


AbstractReportFactory = abstract_report_factory