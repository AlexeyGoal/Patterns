from abc import ABC



# Абстрактный класс для реализации загрузки и обработки данных
class abstract_manager(ABC):
    
    __file_name:str = ""
    
    __is_loaded:bool = False
    
    __data:list = []

    """
    Загрузка данных из файла. 
    """    
    def load(self,file_name:str = "") -> None:
        pass


    """
    Обработка загруженных данных.
    """
    def convert(self) -> bool:
        return False


    """
    Флаг данные подготовленные
    """
    @property
    def is_loaded(self) -> bool:
        return self.__is_loaded