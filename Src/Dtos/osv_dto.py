from Src.Core.exception import arguments_exception


"""
DTO для описания строки оборотно-сальдовой ведомости (ОСВ).
"""
class osv_dto:
    """
    Строка ОСВ по одной позиции номенклатуры.

    DTO хранит начальный остаток, приход, расход, единицу измерения и
    вычисляемый конечный остаток. DTO не зависит от источника данных и
    от формата сериализации.
    """

    """Конструктор строки ОСВ"""
    def __init__(
        self,
        code: str = "",
        name: str = "",
        unit: str = "",
        opening_balance: float = 0.0,
        income: float = 0.0,
        outcome: float = 0.0,
    ):

        self.__code = str(code or "")
        self.__name = str(name or "").strip()
        self.__unit = str(unit or "").strip()
        self.__opening_balance = self.__to_number(opening_balance, "opening_balance")
        self.__income = self.__to_number(income, "income")
        self.__outcome = self.__to_number(outcome, "outcome")

    """Код позиции номенклатуры"""
    @property
    def code(self) -> str:
        return self.__code

    """Наименование позиции номенклатуры"""
    @property
    def name(self) -> str:
        return self.__name

    """Единица измерения позиции"""
    @property
    def unit(self) -> str:
        return self.__unit

    """Начальный остаток"""
    @property
    def opening_balance(self) -> float:
        return self.__opening_balance

    """Приход за период"""
    @property
    def income(self) -> float:
        return self.__income

    """Расход за период"""
    @property
    def outcome(self) -> float:
        return self.__outcome

    """Конечный остаток"""
    @property
    def closing_balance(self) -> float:
        return self.__opening_balance + self.__income - self.__outcome

    """Добавить приход к строке"""
    def add_income(self, value: float) -> "osv_dto":

        self.__income += self.__to_number(value, "income")
        return self

    """Добавить расход к строке"""
    def add_outcome(self, value: float) -> "osv_dto":

        self.__outcome += self.__to_number(value, "outcome")
        return self

    """Установить начальный остаток"""
    def set_opening_balance(self, value: float) -> "osv_dto":

        self.__opening_balance = self.__to_number(value, "opening_balance")
        return self

    """Сериализовать строку ОСВ"""
    def to_dict(self) -> dict:

        return {
            "code": self.__code,
            "name": self.__name,
            "unit": self.__unit,
            "opening_balance": self.__opening_balance,
            "income": self.__income,
            "outcome": self.__outcome,
            "closing_balance": self.closing_balance,
        }

    """Проверить и привести числовое значение"""
    @staticmethod
    def __to_number(value: object, field_name: str) -> float:

        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise arguments_exception(field_name, f"{field_name} must be int or float")

        return float(value)


OsvDto = osv_dto
