"""
Модель нейтрального табличного представления источника данных для отчета
"""
class report_table_dto:
    """
    Нейтральное табличное представление сущности для форматирования отчетом любого формата.

    Параметры конструктора:
        tag: Имя сущности для XML (корневой тег), например recipe / nomenclature / unit
        title: Наименование сущности
        attributes: Дополнительные атрибуты сущности {ключ: значение}
        columns: Колонки таблицы - список кортежей (ключ, заголовок)
        rows: Данные - список словарей {ключ колонки: значение}
    """

    def __init__(self, tag: str = "item", title: str = "", attributes: dict = None,
                 columns: list = None, rows: list = None):

        self.tag = tag
        self.title = title
        self.attributes = attributes if attributes is not None else {}
        self.columns = columns if columns is not None else []
        self.rows = rows if rows is not None else []

    """Ключи колонок в порядке вывода"""
    @property
    def keys(self) -> list:

        return [key for key, _title in self.columns]


ReportTableDto = report_table_dto
