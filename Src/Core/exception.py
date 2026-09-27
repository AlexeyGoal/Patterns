
"""Пользовательское исключение для некорректных аргументов"""
class arguments_exception(Exception):
    
    
    """Конструктор исключения"""
    def __init__(self, field="", message="", stack_trace=""):
    
        self.__field = str(field).strip() if field is not None else ""
        self.__message = str(message).strip() if message is not None else ""
        self.__stack_trace = str(stack_trace).strip() if stack_trace is not None else ""
        super().__init__(str(self))


    """Строковое представление ошибки"""
    def __str__(self):
        
        parts = [f"Error: Inccorect argument! {self.__field}".strip()]
        if self.__message:
            parts.append(self.__message)
        if self.__stack_trace:
            parts.append(self.__stack_trace)
        return "\n".join(parts)



 """Исключение при превышении максимальной длины строкового поля"""
    
class max_length_exception(argument_exception):
    
    """Конструктор исключения превышения длины"""
    def __init__(self, field="", current_length=0, max_length=0):
        
        self.__current_length = current_length
        self.__max_length = max_length
        message = (
            f"Maximum field length exceeded!"
            f"Current: {current_length}, Max: {max_length}"
        )
        super().__init__(field, message)

    """Геттер текущей длины значения поля"""
    @property
    def current_length(self):
        return self.__current_length


    """Геттер максимально допустимой длины поля"""
    @property
    def max_length(self):
        return self.__max_length
