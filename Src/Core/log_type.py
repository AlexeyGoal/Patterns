from enum import Enum


"""
Категории событий журнала аудита.
"""
class log_category(str, Enum):
    # CRUD-операции над доменными сущностями
    CRUD = "CRUD"
    # Складские операции и складская отчетность
    WAREHOUSE = "WAREHOUSE"
    # Вызовы Web-методов (HTTP-запросы)
    WEB = "WEB"
    # Изменение параметров настроек
    SETTINGS = "SETTINGS"


"""
Операции, которые фиксируются в журнале.
"""
class log_operation(str, Enum):
    CREATE = "CREATE"
    READ = "READ"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    REPORT = "REPORT"
    CALL = "CALL"
    LOAD = "LOAD"


"""
Результат выполнения операции.
"""
class log_status(str, Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"


LogCategory = log_category
LogOperation = log_operation
LogStatus = log_status
