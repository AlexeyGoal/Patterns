from Src.Core.abstract_report import abstract_report, AbstractReport
from Src.Core.entity import entity
from Src.Core.validator import validator
from Src.Dtos.report_result_dto import report_result_dto
from Src.Logics.report_source_builder import report_source_builder


"""
Реализация текстового представления отчета
"""
class text_report(abstract_report):
    """
    Класс построения отчета в текстовом формате.
    Рендерит нейтральную таблицу (report_table_dto) из report_source_builder.
    """

    mimetype = "text/plain"
    is_download = False
    extension = "txt"

    def build(self, source) -> report_result_dto:
        """
        Формирует текстовый отчет по переданной сущности.
        :param source: Модель сущности (наследник entity)
        :return: report_result_dto с текстовым представлением
        """
        validator.validate(source, entity)

        table = report_source_builder.build(source)

        lines = [" | ".join(title for _, title in table.columns)]

        for row in table.rows:
            lines.append(" | ".join(str(row[key]) for key in table.keys))

        result = report_result_dto()
        result.text = "\n".join(lines)

        return result


TextReport = text_report
