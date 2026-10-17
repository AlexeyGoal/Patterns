from Src.Core.abstract_report import abstract_report, AbstractReport
from Src.Models.recipe_model import recipe_model
from Src.Core.validator import validator
from Src.Dtos.report_result_dto import report_result_dto
from Src.Logics.entity_fields import extract_entity_fields


"""
Реализация текстового представления отчета по рецепту
"""
class text_report(abstract_report):
    """
    Класс построения отчета по технологической карте (рецепту) в текстовом формате.
    Поддерживает также номенклатуру, единицу измерения и склад.
    """
    __receipt: recipe_model = None

    def build(self, source) -> report_result_dto:
        """
        Формирует текстовый отчет по переданной модели.
        :param source: Модель рецепта (recipe_model) или иной сущности
        :return: report_result_dto с текстовым представлением
        """
        # Отчет по сущности, отличной от рецепта (номенклатура, единица измерения, склад)
        if not isinstance(source, recipe_model):
            fields = extract_entity_fields(source)
            text = "\n".join(f"{name}: {value}" for name, value in fields)

            result = report_result_dto()
            result.text = text
            return result

        validator.validate(source, recipe_model)
        self.__receipt = source

        header = "Код | Наименование | Брутто | Нетто"
        rows_data = []

        for item in self.__receipt.items:
            rows_data.append(f"{item.unique_code} | {item.name} | {item.brutto} | {item.netto}")

        data = "\n".join(rows_data)
        text = f"{header}\n{data}" if data else header

        result = report_result_dto()
        result.text = text

        return result


TextReport = text_report