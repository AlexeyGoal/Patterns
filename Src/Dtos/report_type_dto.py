from enum import Enum


"""
Типы отчетов
"""
class report_type_dto(Enum):
    """
    Перечисление поддерживаемых типов отчетов.
    """

    """
    Текстовый формат
    """
    TXT = 1

    """CSV формат"""
    CSV = 2

    """Markdown формат"""
    MARKDOWN = 3

    """XML формат"""
    XML = 4

    """HTML формат"""
    HTML = 5

ReportTypeEnum = report_type_dto