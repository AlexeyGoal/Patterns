from Src.Core.abstract_report_factory import abstract_report_factory, AbstractReportFactory
from Src.Core.abstract_report import abstract_report, AbstractReport
from Src.Dtos.report_type_dto import report_type_dto, ReportTypeEnum
from Src.Logics.text_factory import text_report, TextReport
from Src.Logics.csv_report import csv_report, CsvReport
from Src.Logics.markdown_report import markdown_report, MarkdownReport
from Src.Logics.xml_report import xml_report, XmlReport
from Src.Logics.html_report import html_report, HtmlReport
from Src.Logics.settings_manager import settings_manager
from Src.Core.exception import arguments_exception


"""
Реализация фабрики для построения отчетов
"""
class report_factory(abstract_report_factory):
    """
    Фабрика для создания и подбора отчетов на основе перечисления report_type_dto.
    Инкапсулирует настройки приложения для определения формата отчета по умолчанию.
    """

    # Маппинг: тип отчета -> класс реализации
    _mapping: dict[report_type_dto, type[abstract_report]]

    # Маппинг: формат ответа из настроек -> тип отчета
    _format_mapping: dict[str, report_type_dto]

    # Менеджер настроек (singleton)
    _settings: settings_manager = None

    def __init__(self):
        """
        Инициализация фабрики, регистрация сопоставлений типов отчетов
        и загрузка настроек приложения.
        """
        self._settings = settings_manager()
        self._settings.load()

        self._mapping = {}
        self._mapping[report_type_dto.TXT] = text_report
        self._mapping[report_type_dto.CSV] = csv_report
        self._mapping[report_type_dto.MARKDOWN] = markdown_report
        self._mapping[report_type_dto.XML] = xml_report
        self._mapping[report_type_dto.HTML] = html_report

        self._format_mapping = {
            "TXT": report_type_dto.TXT,
            "CSV": report_type_dto.CSV,
            "Markdown": report_type_dto.MARKDOWN,
            "XML": report_type_dto.XML,
            "HTML": report_type_dto.HTML,
        }

    def create(self, report_type: report_type_dto) -> abstract_report:
        """
        Создает экземпляр отчета по переданному типу.
        :param report_type: Тип отчета из report_type_dto
        :return: Экземпляр соответствующего класса отчета
        :raises argument_exception: Если тип отчета не реализован или не передан
        """
        if report_type not in self._mapping:
            raise argument_exception("report_type", f"Указанный тип отчета {report_type} не реализован!")

        report_cls = self._mapping[report_type]
        return report_cls() if isinstance(report_cls, type) else report_cls

    def create_default(self) -> abstract_report:
        """
        Создает отчет по умолчанию на основе настроек приложения (response_format).
        :return: Экземпляр соответствующего класса отчета
        :raises argument_exception: Если формат не реализован
        """
        response_format = self._settings.settings.response_format
        report_type = self._format_mapping.get(response_format)

        if report_type is None:
            raise argument_exception(
                "response_format",
                f"Формат ответа '{response_format}' не поддерживается!"
            )

        return self.create(report_type)


# Алиасы для соблюдения стандартов и совместимости
ReportFactory = report_factory