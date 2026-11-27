import datetime

from Src.Core.exception import arguments_exception
from Src.Dtos.filter_dto import filter_dto
from Src.Dtos.osv_dto import osv_dto
from Src.Logics.filter_prototype import filter_prototype
from Src.Logics.storage_manager import storage_manager
from Src.Models.recipe_item_model import recipe_item_type


"""
Сервис формирования оборотно-сальдовой ведомости (ОСВ).
"""
class osv_service:

    """Тип доменной модели, по которой строится ОСВ"""
    ENTITY_TYPE = "nomenclature"

    """Конструктор сервиса ОСВ"""
    def __init__(
        self,
        manager: storage_manager = None,
        prototype: filter_prototype = None,
        today: datetime.date = None,
    ):

        self.__manager = manager if manager is not None else storage_manager()
        self.__prototype = (
            prototype
            if prototype is not None
            else filter_prototype(source=self.__manager.all)
        )

        if today is None:
            self.__today = datetime.date.today
        elif callable(today):
            self.__today = today
        else:
            self.__today = lambda: today

    """Сформировать строки ОСВ с учетом фильтрации"""
    def build(
        self,
        query: filter_dto,
        start_date: object = None,
    ) -> list[osv_dto]:

        if not isinstance(query, filter_dto):
            raise arguments_exception("query", "Ожидался DTO фильтрации")

        if query.entity_type != self.ENTITY_TYPE:
            raise arguments_exception(
                "entity_type",
                f"ОСВ формируется только по типу '{self.ENTITY_TYPE}', "
                f"а передан тип '{query.entity_type}'",
            )

        # 1. Исходные данные из менеджера
        nomenclatures = self.__nomenclatures()
        recipes = self.__recipes()

        # 2. Начало периода и движения
        end_date = self.__today()
        period_start = self.__resolve_start_date(start_date, end_date)
        movements = self.__collect_movements(nomenclatures, recipes, end_date)

        # 3. Начальные остатки
        opening_balances = self.__opening_balances(nomenclatures, movements, period_start)

        # 4. Универсальный прототип с фильтром
        prototype = self.__prototype.clone(query)
        filtered = prototype.items

        # 5. Движения по отфильтрованным позициям
        turnovers = self.__period_turnovers(filtered, movements, period_start, end_date)

        # 6. DTO строк ОСВ
        rows = []

        for item in filtered:
            income, outcome = turnovers.get(id(item), (0.0, 0.0))
            rows.append(
                osv_dto(
                    code=str(getattr(item, "id", "")),
                    name=str(getattr(item, "name", "")),
                    unit=self.__unit_name(item),
                    opening_balance=opening_balances.get(id(item), 0.0),
                    income=income,
                    outcome=outcome,
                )
            )

        return rows

    """Сериализовать строки ОСВ"""
    @staticmethod
    def serialize(rows: list[osv_dto]) -> list[dict]:

        if not isinstance(rows, list):
            raise arguments_exception("rows", "Ожидался список строк ОСВ")

        return [
            row.to_dict() if isinstance(row, osv_dto) else dict(row)
            for row in rows
        ]

    """Сформировать и сериализовать строки ОСВ"""
    def build_serialized(
        self,
        query: filter_dto,
        start_date: object = None,
    ) -> list[dict]:

        return self.serialize(self.build(query, start_date))

    """Исходная номенклатура из менеджера"""
    def __nomenclatures(self) -> list:

        all_method = getattr(self.__manager, "all", None)

        if callable(all_method):
            return list(all_method("nomenclature") or [])

        collection = getattr(self.__manager, "nomenclatures", {})

        if isinstance(collection, dict):
            return list(collection.values())

        return list(collection or [])

    """Исходные технологические карты из менеджера"""
    def __recipes(self) -> list:

        all_method = getattr(self.__manager, "all", None)

        if callable(all_method):
            return list(all_method("recipe") or [])

        collection = getattr(self.__manager, "recipes", {})

        if isinstance(collection, dict):
            return list(collection.values())

        return list(collection or [])

    """Определить дату начала периода"""
    def __resolve_start_date(
        self,
        value: object,
        end_date: datetime.date,
    ) -> datetime.date:

        if value is None:
            result = end_date.replace(day=1)
        elif isinstance(value, datetime.datetime):
            result = value.date()
        elif isinstance(value, datetime.date):
            result = value
        elif isinstance(value, str):
            try:
                result = datetime.date.fromisoformat(value.strip())
            except ValueError as error:
                raise arguments_exception(
                    "start_date",
                    f"Дата начала периода должна быть в формате YYYY-MM-DD: {error}",
                ) from error
        else:
            raise arguments_exception(
                "start_date",
                "Дата начала периода должна быть date или строкой YYYY-MM-DD",
            )

        if result > end_date:
            raise arguments_exception(
                "start_date",
                "Дата начала периода не может быть позже даты окончания",
            )

        return result

    """Собрать движения по технологическим картам"""
    def __collect_movements(
        self,
        nomenclatures: list,
        recipes: list,
        movement_date: datetime.date,
    ) -> list[tuple]:

        names = {
            str(getattr(item, "name", "")).casefold()
            for item in nomenclatures
            if str(getattr(item, "name", "")).strip() != ""
        }
        movements = []
        visited = set()

        for recipe in recipes:
            self.__collect_recipe_movements(
                recipe,
                names,
                movement_date,
                movements,
                visited,
            )

        return movements

    """Движения по технологической карте"""
    def __collect_recipe_movements(
        self,
        recipe: object,
        names: set,
        movement_date: datetime.date,
        movements: list,
        visited: set,
    ) -> None:

        marker = id(recipe)

        if marker in visited:
            return

        visited.add(marker)

        key = str(getattr(recipe, "name", "")).casefold()
        source_date = self.__movement_date(recipe, movement_date)

        if key in names:
            movements.append((
                source_date,
                key,
                self.__number(getattr(recipe, "gross_weight", 0.0)),
                0.0,
            ))

        for item in getattr(recipe, "items", []) or []:
            self.__collect_item_movements(item, names, source_date, movements, visited)

        for sub_recipe in getattr(recipe, "sub_recipes", []) or []:
            self.__collect_recipe_movements(
                sub_recipe,
                names,
                source_date,
                movements,
                visited,
            )

    """Движения по позиции технологической карты"""
    def __collect_item_movements(
        self,
        item: object,
        names: set,
        movement_date: datetime.date,
        movements: list,
        visited: set,
    ) -> None:

        marker = id(item)

        if marker in visited:
            return

        visited.add(marker)

        key = str(getattr(item, "name", "")).casefold()

        if key in names:
            weight = self.__item_weight(item)

            if getattr(item, "type", None) == recipe_item_type.SEMI_FINISHED:
                # Полуфабрикат выпускается и сразу списывается в родительскую карту
                movements.append((movement_date, key, weight, weight))
            else:
                movements.append((movement_date, key, 0.0, weight))

        for nested in getattr(item, "items", []) or []:
            self.__collect_item_movements(
                nested,
                names,
                movement_date,
                movements,
                visited,
            )

    """Начальные остатки на дату начала периода"""
    def __opening_balances(
        self,
        nomenclatures: list,
        movements: list,
        start_date: datetime.date,
    ) -> dict:

        result = {}

        for item in nomenclatures:
            key = str(getattr(item, "name", "")).casefold()
            balance = 0.0

            for movement_date, movement_key, income, outcome in movements:
                if movement_date < start_date and movement_key == key:
                    balance += income - outcome

            result[id(item)] = balance

        return result

    """Обороты за период по отфильтрованной номенклатуре"""
    def __period_turnovers(
        self,
        nomenclatures: list,
        movements: list,
        start_date: datetime.date,
        end_date: datetime.date,
    ) -> dict:

        result = {}

        for item in nomenclatures:
            key = str(getattr(item, "name", "")).casefold()
            income_total = 0.0
            outcome_total = 0.0

            for movement_date, movement_key, income, outcome in movements:
                if start_date <= movement_date <= end_date and movement_key == key:
                    income_total += income
                    outcome_total += outcome

            result[id(item)] = (income_total, outcome_total)

        return result

    """Единица измерения номенклатуры"""
    @staticmethod
    def __unit_name(item: object) -> str:

        unit = getattr(item, "range", None)
        return str(getattr(unit, "name", "")) if unit is not None else ""

    """Дата движения: дата документа рецепта или дата окончания периода"""
    @staticmethod
    def __movement_date(source: object, default: datetime.date) -> datetime.date:

        value = getattr(source, "date", None)

        if isinstance(value, datetime.datetime):
            return value.date()

        if isinstance(value, datetime.date):
            return value

        return default

    """Вес позиции рецепта с учетом вложенных составляющих"""
    @staticmethod
    def __item_weight(item: object) -> float:

        calculator = getattr(item, "calculate_weight", None)

        if callable(calculator):
            return osv_service.__number(calculator())

        return osv_service.__number(getattr(item, "weight", 0.0))

    """Привести значение к числу"""
    @staticmethod
    def __number(value: object) -> float:

        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return 0.0

        return float(value)


OsvService = osv_service
