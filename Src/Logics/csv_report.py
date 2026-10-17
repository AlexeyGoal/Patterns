from Src.Core.abstract_report import abstract_report, AbstractReport
from Src.Models.recipe_model import recipe_model
from Src.Core.validator import validator
from Src.Dtos.report_result_dto import report_result_dto
from Src.Logics.entity_fields import extract_entity_fields


"""
Реализация CSV представления отчета по рецепту
"""
class csv_report(abstract_report):
    """
    Класс построения отчета по технологической карте (рецепту) в CSV формате.
    Поддерживает также номенклатуру, единицу измерения и склад.
    """
    __receipt: recipe_model = None

    def build(self, source) -> report_result_dto:
        """
        Формирует CSV отчет по переданной модели.
        :param source: Модель рецепта (recipe_model) или иной сущности
        :return: report_result_dto с CSV представлением в бинарных данных (UTF-8)
        """
        # Отчет по сущности, отличной от рецепта (номенклатура, единица измерения, склад)
        if not isinstance(source, recipe_model):
            separator = ";"
            fields = extract_entity_fields(source)
            rows = [separator.join(["Поле", "Значение"])]
            rows.extend(separator.join([str(name), str(value)]) for name, value in fields)

            result = report_result_dto()
            result.binary = list("\n".join(rows).encode("utf-8"))
            return result

        validator.validate(source, recipe_model)
        self.__receipt = source

        separator = ";"
        header = separator.join(["Код", "Наименование", "Брутто", "Нетто"])
        rows_data = []

        for item in self.__receipt.items:
            rows_data.append(separator.join([
                str(item.unique_code),
                str(item.name).replace(separator, ","),
                str(item.brutto),
                str(item.netto)
            ]))

        data = "\n".join(rows_data)
        text = f"{header}\n{data}" if data else header

        # CSV формируется в виде бинарных данных (UTF-8) для скачивания файла через API
        result = report_result_dto()
        result.binary = list(text.encode("utf-8"))

        return result


CsvReport = csv_report
