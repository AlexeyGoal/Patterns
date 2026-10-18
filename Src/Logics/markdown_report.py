from Src.Core.abstract_report import abstract_report, AbstractReport
from Src.Core.entity import entity
from Src.Core.validator import validator
from Src.Dtos.report_result_dto import report_result_dto
from Src.Logics.report_source_builder import report_source_builder


"""
Реализация Markdown представления отчета
"""
class markdown_report(abstract_report):
    """
    Класс построения отчета в Markdown формате.
    Рендерит нейтральную таблицу (report_table_dto) из report_source_builder.
    Результат формируется в виде бинарных данных (UTF-8).
    """

    mimetype = "text/markdown"
    is_download = True
    extension = "md"

    def build(self, source) -> report_result_dto:
        """
        Формирует Markdown отчет по переданной сущности.
        :param source: Модель сущности (наследник entity)
        :return: report_result_dto с Markdown представлением в бинарных данных (UTF-8)
        """
        validator.validate(source, entity)

        table = report_source_builder.build(source)

        header = "| " + " | ".join(title for _, title in table.columns) + " |"
        separator = "|" + "-----|" * len(table.columns)
        lines = [header, separator]

        for row in table.rows:
            values = [str(row[key]).replace("|", "\\|") for key in table.keys]
            lines.append("| " + " | ".join(values) + " |")

        # Markdown формируется в виде бинарных данных (UTF-8) для скачивания файла через API
        result = report_result_dto()
        result.binary = list("\n".join(lines).encode("utf-8"))

        return result


MarkdownReport = markdown_report
