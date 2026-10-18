from Src.Core.abstract_report import abstract_report, AbstractReport
from Src.Core.entity import entity
from Src.Core.validator import validator
from Src.Dtos.report_result_dto import report_result_dto
from Src.Logics.report_source_builder import report_source_builder
from xml.sax.saxutils import escape


"""
Реализация HTML представления отчета
"""
class html_report(abstract_report):
    """
    Класс построения отчета в HTML формате.
    Рендерит нейтральную таблицу (report_table_dto) из report_source_builder.
    """

    mimetype = "text/html"
    is_download = False
    extension = "html"

    def build(self, source) -> report_result_dto:
        """
        Формирует HTML отчет по переданной сущности.
        :param source: Модель сущности (наследник entity)
        :return: report_result_dto с HTML представлением
        """
        validator.validate(source, entity)

        table = report_source_builder.build(source)

        lines = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            '  <meta charset="UTF-8">',
            "  <title>Отчет</title>",
            "  <style>",
            "    table { border-collapse: collapse; width: 100%; }",
            "    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }",
            "    th { background-color: #f2f2f2; }",
            "  </style>",
            "</head>",
            "<body>",
        ]

        # Заголовок и реквизиты сущности над таблицей
        if table.title:
            lines.append(f"  <h2>{escape(str(table.title))}</h2>")

        for key, value in table.attributes.items():
            lines.append(f"  <p><b>{escape(str(key))}</b>: {escape(str(value))}</p>")

        lines.append("  <table>")
        lines.append("    <tr>" + "".join(
            f"<th>{escape(str(title))}</th>" for _, title in table.columns
        ) + "</tr>")

        for row in table.rows:
            lines.append("    <tr>" + "".join(
                f"<td>{escape(str(row[key]))}</td>" for key in table.keys
            ) + "</tr>")

        lines.extend([
            "  </table>",
            "</body>",
            "</html>"
        ])

        result = report_result_dto()
        result.text = "\n".join(lines)

        return result


HtmlReport = html_report
