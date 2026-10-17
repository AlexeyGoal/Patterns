from Src.Core.abstract_report import abstract_report, AbstractReport
from Src.Models.recipe_model import recipe_model
from Src.Core.validator import validator
from Src.Dtos.report_result_dto import report_result_dto
from Src.Logics.entity_fields import extract_entity_fields
from xml.sax.saxutils import escape


"""
Реализация XML представления отчета по рецепту
"""
class xml_report(abstract_report):
    """
    Класс построения отчета по технологической карте (рецепту) в XML формате.
    Поддерживает также номенклатуру, единицу измерения и склад.
    """
    __receipt: recipe_model = None

    def build(self, source) -> report_result_dto:
        """
        Формирует XML отчет по переданной модели.
        :param source: Модель рецепта (recipe_model) или иной сущности
        :return: report_result_dto с XML представлением
        """
        # Отчет по сущности, отличной от рецепта (номенклатура, единица измерения, склад)
        if not isinstance(source, recipe_model):
            lines = ['<?xml version="1.0" encoding="UTF-8"?>']
            lines.append('<report>')
            for name, value in extract_entity_fields(source):
                lines.append(f'  <field name="{escape(str(name))}">{escape(str(value))}</field>')
            lines.append('</report>')

            result = report_result_dto()
            result.text = "\n".join(lines)
            return result

        validator.validate(source, recipe_model)
        self.__receipt = source

        lines = ['<?xml version="1.0" encoding="UTF-8"?>']
        lines.append('<report>')
        lines.append('  <items>')

        for item in self.__receipt.items:
            lines.append('    <item>')
            lines.append(f'      <code>{escape(str(item.unique_code))}</code>')
            lines.append(f'      <name>{escape(str(item.name))}</name>')
            lines.append(f'      <brutto>{item.brutto}</brutto>')
            lines.append(f'      <netto>{item.netto}</netto>')
            lines.append('    </item>')

        lines.append('  </items>')
        lines.append('</report>')

        text = "\n".join(lines)

        result = report_result_dto()
        result.text = text

        return result


XmlReport = xml_report
