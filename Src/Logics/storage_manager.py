from Src.Core.abstract_manager import abstract_manager
from Src.Core.validator import validator
from Src.Logics.settings_manager import settings_manager
from Src.Models.storage_model import storage_model
from Src.Models.range_model import range_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.nomenclature_group_model import nomenclature_group_model


# Менеджер хранения доменных моделей.
class storage_manager(abstract_manager):
   
    _storages: dict = None
    _ranges: dict = None
    _nomenclatures: dict = None
    _groups: dict = None
    __is_initialized: bool = False

    # Singleton
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(storage_manager, cls).__new__(cls)
            cls.instance._storages = {}
            cls.instance._ranges = {}
            cls.instance._nomenclatures = {}
            cls.instance._groups = {}
            cls.instance.__is_initialized = False
        return cls.instance


    # Переопределенный метод abstract_manager
    def convert(self, settings=None) -> bool:
        
        if self.__is_initialized:
            return True

        try:
            if settings is None:
                s_manager = settings_manager()
                if not s_manager.is_loaded:
                    s_manager.load()
                settings = s_manager.settings

            if settings and settings.is_first_start:
                self._initialize_primary_data()

            self.__is_initialized = True
            return True
        except Exception:
            return False


    # Инициализация первичных данных 
    def _initialize_primary_data(self) -> None:
        
        self.__create_ranges()
        self.__create_groups()
        self.__create_nomenclatures()
        self.__create_storages()

    # Генерация базовых и производных единиц измерения
    def __create_ranges(self) -> None:
        
        gram = range_model(name="грамм", conversion_factor=1, base_range=None)
        kilogram = range_model(name="килограмм", conversion_factor=1000, base_range=gram)
        piece = range_model(name="штука", conversion_factor=1, base_range=None)
        liter = range_model(name="литр", conversion_factor=1, base_range=None)
        milliliter = range_model(name="миллилитр", conversion_factor=0.001, base_range=liter)

        for r in (gram, kilogram, piece, liter, milliliter):
            self.add_range(r)


    # Генерация групп номенклатуры под технологическую карту
    def __create_groups(self) -> None:
        
        grocery = nomenclature_group_model(name="Бакалея")
        dairy = nomenclature_group_model(name="Молочные продукты")
        dishes = nomenclature_group_model(name="Блюда")

        self.add_group(grocery)
        self.add_group(dairy)
        self.add_group(dishes)


    # Генерация номенклатуры.
    def __create_nomenclatures(self) -> None:
        """"""
        groups_by_name = {g.name: g for g in self._groups.values()}
        ranges_by_name = {r.name: r for r in self._ranges.values()}

        grocery = groups_by_name.get("Бакалея")
        dairy = groups_by_name.get("Молочные продукты")
        dishes = groups_by_name.get("Блюда")

        kg = ranges_by_name.get("килограмм")
        liter = ranges_by_name.get("литр")
        piece = ranges_by_name.get("штука")

        items = [
            nomenclature_model("Мука пшеничная", "Мука пшеничная высший сорт", grocery, kg),
            nomenclature_model("Молоко 3.2%", "Молоко коровье пастеризованное 3.2%", dairy, liter),
            nomenclature_model("Яйца куриные", "Яйца куриные столовые С0", dairy, piece),
            nomenclature_model("Масло сливочное", "Масло сливочное крестьянское 72.5%", dairy, kg),
            nomenclature_model("Сахар", "Сахар белый кристаллический", grocery, kg),
            nomenclature_model("Соль", "Соль поваренная пищевая", grocery, kg),
            nomenclature_model("Блины классические", "Блины классические тонкие", dishes, piece),
        ]

        for item in items:
            self.add_nomenclature(item)
    
    # Генерация складов
    def __create_storages(self) -> None:
        
        main_storage = storage_model(name="Основной склад", address="ул. Промышленная, 5, пом. 101")
        fridge = storage_model(name="Холодильник цеха", address="ул. Промышленная, 5, пом. 102")

        self.add_storage(main_storage)
        self.add_storage(fridge)


    # Добавить склад
    def add_storage(self, item: storage_model) -> bool:
        
        if not isinstance(item, storage_model) or item.id in self._storages:
            return False
        self._storages[item.id] = item
        return True


    # Добавить единицу измерения
    def add_range(self, item: range_model) -> bool:
        
        if not isinstance(item, range_model) or item.id in self._ranges:
            return False
        self._ranges[item.id] = item
        return True

    # Добавить позицию номенклатуры
    def add_nomenclature(self, item: nomenclature_model) -> bool:
        
        if not isinstance(item, nomenclature_model) or item.id in self._nomenclatures:
            return False
        self._nomenclatures[item.id] = item
        return True


    # Добавить группу номенклатуры
    def add_group(self, item: nomenclature_group_model) -> bool:
        
        if not isinstance(item, nomenclature_group_model) or item.id in self._groups:
            return False
        self._groups[item.id] = item
        return True
    

    # Словарь складов
    @property
    def storages(self) -> dict:
        
        return self._storages

    # Словарь единиц измерения
    @property
    def ranges(self) -> dict:
        
        return self._ranges


    # Словарь номенклатуры
    @property
    def nomenclatures(self) -> dict:
        return self._nomenclatures
    

    # Словарь групп номенклатуры
    @property
    def groups(self) -> dict:
        
        return self._groups


    # Все данные хранилища по категориям
    @property
    def data(self) -> dict:
       
        return {
            "storages": self._storages,
            "ranges": self._ranges,
            "nomenclatures": self._nomenclatures,
            "groups": self._groups
        }


    # Флаг завершения инициализации
    @property
    def is_initialized(self) -> bool:
        
        return self.__is_initialized

    # Флаг готовности данных
    @property
    def is_loaded(self) -> bool:
        
        return self.__is_initialized