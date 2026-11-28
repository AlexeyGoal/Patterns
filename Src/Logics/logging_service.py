import os

from Src.Core.abstract_subject import abstract_subject
from Src.Dtos.log_event_dto import log_event_dto
from Src.Logics.file_log_observer import file_log_observer
from Src.Logics.memory_log_observer import memory_log_observer


"""
Сервис логирования
"""
class logging_service(abstract_subject):

    __instance = None
    __initialized = False


    """Singleton: единый журнал на всё приложение"""
    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(logging_service, cls).__new__(cls)
        return cls.__instance


    """Инициализация подписчиков по умолчанию"""
    def __init__(self) -> None:
        if logging_service.__initialized:
            return

        super().__init__()
        self.__memory = None
        self.__configure_default_observers()
        logging_service.__initialized = True


    """Наблюдатель, хранящий события в памяти"""
    @property
    def memory(self) -> memory_log_observer:
        return self.__memory


    """Записать событие в журнал и разослать его наблюдателям"""
    def log(self, event: log_event_dto) -> log_event_dto:

        if not isinstance(event, log_event_dto):
            raise TypeError("Ожидалось событие log_event_dto")

        self.notify(event)
        return event


    """Последние события журнала в JSON-совместимом виде"""
    def events(
        self,
        category: str = None,
        status: str = None,
        limit: int = None,
    ) -> list[dict]:

        if self.__memory is None:
            return []

        return self.__memory.to_dicts(
            category=category,
            status=status,
            limit=limit,
        )


    """Очистить журнал в памяти"""
    def clear(self) -> None:
        if self.__memory is not None:
            self.__memory.clear()


    """Сбросить подписчиков и заново подключить наблюдатели по умолчанию"""
    def reset(self) -> None:
        self.detach_all()
        self.__memory = None
        self.__configure_default_observers()


    """Подключить наблюдатели по умолчанию"""
    def __configure_default_observers(self) -> None:

        self.__memory = memory_log_observer()
        self.attach(self.__memory)

        self.attach(file_log_observer(self.__resolve_log_file()))

        console_flag = os.environ.get("AUDIT_LOG_CONSOLE", "").strip().lower()

        if console_flag in ("1", "true", "yes", "on"):
            from Src.Logics.console_log_observer import console_log_observer
            self.attach(console_log_observer())


    """Путь к файлу журнала с учетом переменной окружения"""
    @staticmethod
    def __resolve_log_file() -> str:

        configured = os.environ.get("AUDIT_LOG_FILE", "").strip()

        if configured:
            return configured

        project_root = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )

        return os.path.join(project_root, "logs", "audit.json")


LoggingService = logging_service
