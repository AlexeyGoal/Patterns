from Src.Core.abstract_report import abstract_report, AbstractReport
from Src.Core.entity import entity
from Src.Core.validator import validator
from Src.Dtos.report_result_dto import report_result_dto
from Src.Logics.report_source_builder import report_source_builder
from xml.sax.saxutils import escape


"""
Реализация XML представления отчета
"""
class xml_report(abstract_report):
    """
    Класс построения отчета в XML формате.
    Рендерит нейтральную таблицу (report_table_dto) из report_source_builder.
    """

    mimetype = "application/xml"
    is_download = False
    extension = "xml"

    def build(self, source) -> report_result_dto:
        """
        Формирует XML отчет по переданной сущности.
        :param source: Модель сущности (наследник entity)
        :return: report_result_dto с XML представлением
        """
        validator.validate(source, entity)

        table = report_source_builder.build(source)

        lines = ['<?xml version="1.0" encoding="UTF-8"?>']
        lines.append('<report>')

        # Реквизиты сущности, не входящие в табличную часть
        for key, value in table.attributes.items():
            lines.append(f'  <field name="{escape(str(key))}">{escape(str(value))}</field>')

        lines.append('  <items>')

        for row in table.rows:
            lines.append('    <item>')
            for key in table.keys:
                lines.append(f'      <{key}>{escape(str(row[key]))}</{key}>')
            lines.append('    </item>')

        lines.append('  </items>')
        lines.append('</report>')

        result = report_result_dto()
        result.text = "\n".join(lines)

        return result


XmlReport = xml_report
