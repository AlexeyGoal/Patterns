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
    Фабрика для создания и подбора отчетов на основе перечисления report_type_dto
    или строкового имени формата (для API и настроек приложения).
    Инкапсулирует настройки приложения для определения формата отчета по умолчанию.
    """

    # Маппинг: тип отчета -> класс реализации
    _mapping: dict[report_type_dto, type[abstract_report]]

    # Маппинг: строковое имя формата -> тип отчета
    _names: dict[str, report_type_dto]

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

        self._names = {
            "txt": report_type_dto.TXT,
            "text": report_type_dto.TXT,
            "csv": report_type_dto.CSV,
            "markdown": report_type_dto.MARKDOWN,
            "xml": report_type_dto.XML,
            "html": report_type_dto.HTML,
        }

    @property
    def supported_formats(self) -> list:
        """
        Список поддерживаемых строковых имен форматов.
        """
        return list(self._names.keys())

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

    def create_by_name(self, name: str) -> abstract_report:
        """
        Создает экземпляр отчета по строковому имени формата (регистронезависимо).
        :param name: Имя формата (например, "csv" или "Markdown")
        :return: Экземпляр отчета или None, если формат не поддерживается
        """
        if name is None:
            return None

        report_type = self._names.get(str(name).strip().lower())
        if report_type is None:
            return None

        return self.create(report_type)

    def create_default(self) -> abstract_report:
        """
        Создает отчет по умолчанию на основе настроек приложения (response_format).
        Формат определяется по строковому имени (регистронезависимо).
        :return: Экземпляр соответствующего класса отчета
        :raises argument_exception: Если формат не реализован
        """
        response_format = self._settings.settings.response_format
        report = self.create_by_name(response_format)

        if report is None:
            raise argument_exception(
                "response_format",
                f"Формат ответа '{response_format}' не поддерживается!"
            )

        return report


# Алиасы для соблюдения стандартов и совместимости
ReportFactory = report_factory
