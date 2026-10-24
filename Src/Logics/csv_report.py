from Src.Core.abstract_report import abstract_report, AbstractReport
from Src.Core.entity import entity
from Src.Core.validator import validator
from Src.Dtos.report_result_dto import report_result_dto
from Src.Logics.report_source_builder import report_source_builder


"""
Реализация CSV представления отчета
"""
class csv_report(abstract_report):
    """
    Класс построения отчета в CSV формате.
    Рендерит нейтральную таблицу (report_table_dto) из report_source_builder.
    Результат формируется в виде бинарных данных (UTF-8).
    """

    mimetype = "text/csv"
    is_download = True
    extension = "csv"

    def build(self, source) -> report_result_dto:
        """
        Формирует CSV отчет по переданной сущности.
        :param source: Модель сущности (наследник entity)
        :return: report_result_dto с CSV представлением в бинарных данных (UTF-8)
        """
        validator.validate(source, entity)

        separator = ";"
        table = report_source_builder.build(source)

        lines = [separator.join(title for _, title in table.columns)]

        for row in table.rows:
            lines.append(separator.join(
                str(row[key]).replace(separator, ",") for key in table.keys
            ))

        # CSV формируется в виде бинарных данных (UTF-8) для скачивания файла через API
        result = report_result_dto()
        result.binary = list("\n".join(lines).encode("utf-8"))

        return result


CsvReport = csv_report
