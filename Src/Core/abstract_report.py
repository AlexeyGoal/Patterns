from abc import ABC, abstractmethod
from Src.Dtos.report_result_dto import report_result_dto


"""
Абстрактный класс для формирования отчета
"""
class abstract_report(ABC):
    """
    Базовый абстрактный класс стратегии/компонента формирования отчета.

    Каждый наследник сам знает, как его результат доставляется через API:
    MIME-тип, расширение файла и режим скачивания.
    """

    @property
    @abstractmethod
    def mimetype(self) -> str:
        """
        MIME-тип результата отчета (например, "text/csv").
        Charset подставляется в HTTP-заголовок автоматически.
        """
        pass

    @property
    @abstractmethod
    def is_download(self) -> bool:
        """
        Отдавать ли отчет скачиванием файла (True) или структурированным текстом (False).
        """
        pass

    @property
    @abstractmethod
    def extension(self) -> str:
        """
        Расширение файла отчета для скачивания (например, "csv", "md").
        """
        pass

    @abstractmethod
    def build(self, source) -> report_result_dto:
        """
        Сформировать отчет по переданному источнику данных.
        :param source: Доменная модель-источник данных для отчета
        :return: Экземпляр report_result_dto с результатом
        """
        pass


AbstractReport = abstract_report
