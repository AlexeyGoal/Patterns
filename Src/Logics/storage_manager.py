from Src.Core.abstract_manager import abstract_manager
from Src.Core.validator import validator
from Src.Logics.settings_manager import settings_manager
from Src.Models.storage_model import storage_model
from Src.Models.range_model import range_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.recipe_model import recipe_model


# Менеджер хранения доменных моделей.
class storage_manager(abstract_manager):
   
    _storages: dict = None
    _ranges: dict = None
    _nomenclatures: dict = None
    _groups: dict = None
    _recipes: dict = None
    __is_initialized: bool = False

    # Singleton
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(storage_manager, cls).__new__(cls)
            cls.instance._storages = {}
            cls.instance._ranges = {}
            cls.instance._nomenclatures = {}
            cls.instance._groups = {}
            cls.instance._recipes = {}
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
        self.__create_recipes()

    # Генерация базовых и производных единиц измерения
    def __create_ranges(self) -> None:

        kilogram = range_model.create_kilogram()
        gram = kilogram.base_range
        liter = range_model.create_liter()
        milliliter = liter.base_range
        piece = range_model.create_piece()

        for r in (gram, kilogram, milliliter, liter, piece):
            self.add_range(r)

       


    def __create_groups(self) -> None:

        for group in (
            nomenclature_group_model.create_grocery(),
            nomenclature_group_model.create_dairy(),
            nomenclature_group_model.create_dishes(),
            nomenclature_group_model.create_packaging(),
            nomenclature_group_model.create_meat(),
            nomenclature_group_model.create_vegetables(),
            nomenclature_group_model.create_semi_finished(),
        ):
            self.add_group(group)


    # Генерация номенклатуры.
    def __create_nomenclatures(self) -> None:

        groups_by_name = {g.name: g for g in self._groups.values()}
        ranges_by_name = {r.name: r for r in self._ranges.values()}

        items = [
            nomenclature_model.create_flour(groups_by_name.get("Бакалея"), ranges_by_name.get("килограмм")),
            nomenclature_model.create_milk(groups_by_name.get("Молочные продукты"), ranges_by_name.get("литр")),
            nomenclature_model.create_eggs(groups_by_name.get("Молочные продукты"), ranges_by_name.get("штука")),
            nomenclature_model.create_butter(groups_by_name.get("Молочные продукты"), ranges_by_name.get("килограмм")),
            nomenclature_model.create_sugar(groups_by_name.get("Бакалея"), ranges_by_name.get("килограмм")),
            nomenclature_model.create_salt(groups_by_name.get("Бакалея"), ranges_by_name.get("килограмм")),
            nomenclature_model.create_cottage_cheese(groups_by_name.get("Молочные продукты"), ranges_by_name.get("килограмм")),
            nomenclature_model.create_sunflower_oil(groups_by_name.get("Бакалея"), ranges_by_name.get("литр")),
            nomenclature_model.create_breakfast_box(groups_by_name.get("Упаковка"), ranges_by_name.get("штука")),
            nomenclature_model.create_chicken(groups_by_name.get("Мясные продукты"), ranges_by_name.get("килограмм")),
            nomenclature_model.create_carrot(groups_by_name.get("Овощи"), ranges_by_name.get("килограмм")),
            nomenclature_model.create_onion(groups_by_name.get("Овощи"), ranges_by_name.get("килограмм")),
            nomenclature_model.create_potato(groups_by_name.get("Овощи"), ranges_by_name.get("килограмм")),
            nomenclature_model.create_semi_finished_noodles(groups_by_name.get("Полуфабрикаты"), ranges_by_name.get("килограмм")),
            nomenclature_model.create_sour_cream(groups_by_name.get("Молочные продукты"), ranges_by_name.get("килограмм")),
            nomenclature_model.create_bay_leaf(groups_by_name.get("Бакалея"), ranges_by_name.get("штука")),
            nomenclature_model.create_dish_noodle_soup(groups_by_name.get("Блюда"), ranges_by_name.get("штука")),
        ]

        for item in items:
            self.add_nomenclature(item)


    
    
    # Генерация складов
    def __create_storages(self) -> None:
        
        self.add_storage(storage_model.create_main_storage())
        self.add_storage(storage_model.create_fridge())

    # Генерация рецептов
    def __create_recipes(self) -> None:
        
        recipe = recipe_model.create_first_start_recipe()
        self.add_recipe(recipe)


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

    # Добавить рецепт
    def add_recipe(self, item: recipe_model) -> bool:
        
        if not isinstance(item, recipe_model) or item.id in self._recipes:
            return False
        self._recipes[item.id] = item
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

    # Словарь рецептов
    @property
    def recipes(self) -> dict:
        
        return self._recipes


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