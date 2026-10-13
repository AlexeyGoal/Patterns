from Src.Core.entity import entity
from Src.Core.exception import arguments_exception


"""Модель склада"""
class storage_model(entity):

    """Конструктор склада"""
    def __init__(self, name="", address=""):

        super().__init__()
        self.name = name
        self.address = address

    """Геттер адреса склада"""
    @property
    def address(self):

        return self.__address

    """Сеттер адреса склада"""
    @address.setter
    def address(self, value):

        if not isinstance(value, str):
            raise arguments_exception("address", "address must be str")

        self.__address = value.strip()


    """Фабричный метод - создать Основной склад"""
    @staticmethod
    def create_main_storage():
        return storage_model("Основной склад", "ул. Промышленная, 5, пом. 101")


    """Фабричный метод - создать Холодильник цеха"""
    @staticmethod
    def create_fridge():
        return storage_model("Холодильник цеха", "ул. Промышленная, 5, пом. 102")
