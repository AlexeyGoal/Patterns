from Src.Core.abstract_report import abstract_report, AbstractReport
from Src.Models.recipe_model import recipe_model
from Src.Core.validator import validator
from Src.Dtos.report_result_dto import report_result_dto
from Src.Logics.entity_fields import extract_entity_fields


"""
Реализация Markdown представления отчета по рецепту
"""
class markdown_report(abstract_report):
    """
    Класс построения отчета по технологической карте (рецепту) в Markdown формате.
    Поддерживает также номенклатуру, единицу измерения и склад.
    """
    __receipt: recipe_model = None

    def build(self, source) -> report_result_dto:
        """
        Формирует Markdown отчет по переданной модели.
        :param source: Модель рецепта (recipe_model) или иной сущности
        :return: report_result_dto с Markdown представлением в бинарных данных (UTF-8)
        """
        # Отчет по сущности, отличной от рецепта (номенклатура, единица измерения, склад)
        if not isinstance(source, recipe_model):
            lines = [
                "| Поле | Значение |",
                "|------|----------|"
            ]
            for name, value in extract_entity_fields(source):
                lines.append(f"| {name} | {value} |")

            result = report_result_dto()
            result.binary = list("\n".join(lines).encode("utf-8"))
            return result

        validator.validate(source, recipe_model)
        self.__receipt = source

        lines = [
            "| Код | Наименование | Брутто | Нетто |",
            "|-----|-------------|--------|-------|"
        ]

        for item in self.__receipt.items:
            name = str(item.name).replace("|", "\\|")
            lines.append(f"| {item.unique_code} | {name} | {item.brutto} | {item.netto} |")

        text = "\n".join(lines)

        # Markdown формируется в виде бинарных данных (UTF-8) для скачивания файла через API
        result = report_result_dto()
        result.binary = list(text.encode("utf-8"))

        return result


MarkdownReport = markdown_report
