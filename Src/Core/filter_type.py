from enum import Enum


"""
Варианты сравнения значения поля при фильтрации.
"""
class filter_type(Enum):
    """Полное совпадение значения поля."""
    EQUALS = "equals"

    """Вхождение строки в значение поля."""
    LIKE = "like"
