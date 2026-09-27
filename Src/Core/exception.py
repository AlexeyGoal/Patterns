
class arguments_exception(Exception):
    """
    Пользовательское исключение для некорректных аргументов моделей.
    
    """

    def __init__(self, field="", message="", stack_trace=""):
        """
        Конструктор исключения некорректного аргумента.

        Параметры:
            field: Наименование ошибочного аргумента/поля
            message: Поясняющее сообщение об ошибке
            stack_trace: Стек вызовов (трассировка)
        """
        self.__field = str(field).strip() if field is not None else ""
        self.__message = str(message).strip() if message is not None else ""
        self.__stack_trace = str(stack_trace).strip() if stack_trace is not None else ""
        super().__init__(str(self))


    def __str__(self):
        """
        Строковое представление ошибки.
        """
        parts = [f"Ошибка: Некорректный аргумент! {self.__field}".strip()]
        if self.__message:
            parts.append(self.__message)
        if self.__stack_trace:
            parts.append(self.__stack_trace)
        return "\n".join(parts)


        