from Src.Core.abstract_report import abstract_report, AbstractReport
from Src.Models.recipe_model import recipe_model
from Src.Core.validator import validator
from Src.Dtos.report_result_dto import report_result_dto
from Src.Logics.entity_fields import extract_entity_fields
from xml.sax.saxutils import escape


"""
Реализация HTML представления отчета по рецепту
"""
class html_report(abstract_report):
    """
    Класс построения отчета по технологической карте (рецепту) в HTML формате.
    Поддерживает также номенклатуру, единицу измерения и склад.
    """
    __receipt: recipe_model = None

    def build(self, source) -> report_result_dto:
        """
        Формирует HTML отчет по переданной модели.
        :param source: Модель рецепта (recipe_model) или иной сущности
        :return: report_result_dto с HTML представлением
        """
        # Отчет по сущности, отличной от рецепта (номенклатура, единица измерения, склад)
        if not isinstance(source, recipe_model):
            lines = [
                "<!DOCTYPE html>",
                "<html>",
                "<head>",
                '  <meta charset="UTF-8">',
                "  <title>Отчет по сущности</title>",
                "  <style>",
                "    table { border-collapse: collapse; width: 100%; }",
                "    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }",
                "    th { background-color: #f2f2f2; }",
                "  </style>",
                "</head>",
                "<body>",
                "  <table>",
                "    <tr><th>Поле</th><th>Значение</th></tr>"
            ]
            for name, value in extract_entity_fields(source):
                lines.append(f"    <tr><td>{escape(str(name))}</td><td>{escape(str(value))}</td></tr>")

            lines.extend([
                "  </table>",
                "</body>",
                "</html>"
            ])

            result = report_result_dto()
            result.text = "\n".join(lines)
            return result

        validator.validate(source, recipe_model)
        self.__receipt = source

        lines = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            '  <meta charset="UTF-8">',
            "  <title>Отчет по рецепту</title>",
            "  <style>",
            "    table { border-collapse: collapse; width: 100%; }",
            "    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }",
            "    th { background-color: #f2f2f2; }",
            "  </style>",
            "</head>",
            "<body>",
            "  <table>",
            "    <tr><th>Код</th><th>Наименование</th><th>Брутто</th><th>Нетто</th></tr>"
        ]

        for item in self.__receipt.items:
            lines.append(
                f"    <tr><td>{escape(str(item.unique_code))}</td>"
                f"<td>{escape(str(item.name))}</td>"
                f"<td>{item.brutto}</td>"
                f"<td>{item.netto}</td></tr>"
            )

        lines.extend([
            "  </table>",
            "</body>",
            "</html>"
        ])

        text = "\n".join(lines)

        result = report_result_dto()
        result.text = text

        return result


HtmlReport = html_report
