import datetime

import pytest

import main
from Src.Core.exception import arguments_exception
from Src.Core.filter_type import filter_type
from Src.Dtos.filter_dto import filter_dto
from Src.Dtos.osv_dto import osv_dto
from Src.Logics.entity_filter import entity_filter
from Src.Logics.osv_service import osv_service
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.recipe_item_model import recipe_item_model
from Src.Models.recipe_model import recipe_model


class fake_manager:
    """Минимальный менеджер исходных данных для тестов сервиса ОСВ."""

    def __init__(self, nomenclatures: list, recipes: list = None):
        self.nomenclatures = {item.id: item for item in nomenclatures}
        self.recipes = {item.id: item for item in (recipes or [])}

    def all(self, entity_type: str) -> list:
        """Отдать исходные данные по типу доменной модели."""
        collections = {
            "nomenclature": self.nomenclatures,
            "recipe": self.recipes,
        }

        return list(collections.get(entity_type, {}).values())


class spy_prototype:
    """Прототип-шпион: проверяет, что сервис получает готовый отфильтрованный список."""

    def __init__(self, items: list = None):
        self.query = None
        self.items = list(items or [])
        self.__filter = entity_filter()

    def clone(self, query):
        self.query = query
        return spy_prototype(self.__filter.apply(self.items, query))


@pytest.fixture
def flour_recipe():
    """Технологическая карта, расходующая муку и выпускающая блюдо."""
    flour = nomenclature_model.create_flour()
    dish = nomenclature_model.create_dish_noodle_soup()

    recipe = recipe_model.create("Суп-лапша домашняя", "Тестовый рецепт")
    recipe.add_item(
        recipe_item_model.create_ingredient(
            "Мука пшеничная",
            200,
            range_model.create_gram(),
        )
    )
    recipe.date = datetime.date(2026, 1, 10)

    return flour, dish, recipe


class TestOsvDto:
    """Юнит-тесты DTO строки ОСВ."""

    def test_closing_balance_is_calculated(self):
        """Конечный остаток считается как начало + приход - расход."""
        row = osv_dto(
            code="1",
            name="Мука пшеничная",
            unit="килограмм",
            opening_balance=10,
            income=5,
            outcome=3,
        )

        assert row.closing_balance == 12

    def test_dto_is_serialized_for_api(self):
        """DTO ОСВ преобразуется в JSON-совместимый словарь."""
        row = osv_dto("1", "Мука пшеничная", "килограмм", 1, 2, 3)

        assert row.to_dict() == {
            "code": "1",
            "name": "Мука пшеничная",
            "unit": "килограмм",
            "opening_balance": 1.0,
            "income": 2.0,
            "outcome": 3.0,
            "closing_balance": 0.0,
        }


class TestOsvService:
    """Тесты сервиса формирования ОСВ."""

    def test_service_returns_dto_rows(self, flour_recipe):
        """Сервис формирует DTO строк ОСВ."""
        flour, dish, recipe = flour_recipe
        service = osv_service(
            fake_manager([flour, dish], [recipe]),
            today=datetime.date(2026, 1, 15),
        )
        query = filter_dto("nomenclature", "name", "а", filter_type.LIKE)

        rows = service.build(query)

        assert len(rows) == 2
        assert all(isinstance(row, osv_dto) for row in rows)

    def test_service_uses_universal_filter_prototype(self, flour_recipe):
        """Сервис получает отфильтрованные данные через универсальный прототип."""
        flour, dish, _recipe = flour_recipe
        prototype = spy_prototype([flour, dish])
        service = osv_service(
            fake_manager([flour, dish]),
            prototype=prototype,
            today=datetime.date(2026, 1, 15),
        )
        query = filter_dto("nomenclature", "name", "Мука", filter_type.LIKE)

        rows = service.build(query)

        assert prototype.query is query
        assert len(prototype.items) == 2
        assert [row.name for row in rows] == ["Мука пшеничная"]

    def test_service_calculates_period_turnovers(self, flour_recipe):
        """Приход и расход за период рассчитываются по движениям."""
        flour, dish, recipe = flour_recipe
        service = osv_service(
            fake_manager([flour, dish], [recipe]),
            today=datetime.date(2026, 1, 15),
        )
        query = filter_dto("nomenclature", "name", "а", filter_type.LIKE)

        result = {row.name: row for row in service.build(query)}

        assert result["Мука пшеничная"].opening_balance == 0
        assert result["Мука пшеничная"].outcome == 200
        assert result["Мука пшеничная"].closing_balance == -200
        assert result["Суп-лапша домашняя"].income == 200
        assert result["Суп-лапша домашняя"].closing_balance == 200

    def test_service_calculates_opening_balances(self, flour_recipe):
        """Движения до даты начала периода попадают в начальный остаток."""
        flour, dish, recipe = flour_recipe
        service = osv_service(
            fake_manager([flour, dish], [recipe]),
            today=datetime.date(2026, 1, 15),
        )
        query = filter_dto("nomenclature", "name", "а", filter_type.LIKE)

        result = {
            row.name: row
            for row in service.build(query, start_date=datetime.date(2026, 1, 12))
        }

        assert result["Мука пшеничная"].opening_balance == -200
        assert result["Мука пшеничная"].income == 0
        assert result["Мука пшеничная"].outcome == 0
        assert result["Мука пшеничная"].closing_balance == -200
        assert result["Суп-лапша домашняя"].opening_balance == 200

    def test_service_uses_start_of_month_by_default(self, flour_recipe):
        """Без явной даты период начинается с первого дня текущего месяца."""
        flour, dish, recipe = flour_recipe
        service = osv_service(
            fake_manager([flour, dish], [recipe]),
            today=datetime.date(2026, 1, 15),
        )
        query = filter_dto("nomenclature", "name", "Мука", filter_type.LIKE)

        row = service.build(query)[0]

        assert row.opening_balance == 0
        assert row.outcome == 200

    def test_service_serializes_rows(self, flour_recipe):
        """Сервис сериализует DTO строк ОСВ для API."""
        flour, dish, recipe = flour_recipe
        service = osv_service(
            fake_manager([flour, dish], [recipe]),
            today=datetime.date(2026, 1, 15),
        )
        query = filter_dto("nomenclature", "name", "Мука", filter_type.LIKE)

        rows = service.build_serialized(query)

        assert rows[0]["name"] == "Мука пшеничная"
        assert rows[0]["closing_balance"] == -200

    def test_service_rejects_foreign_entity_type(self):
        """Сервис формирует ОСВ только по номенклатуре."""
        service = osv_service(fake_manager([]))
        query = filter_dto("group", "name", "Бакалея")

        with pytest.raises(arguments_exception):
            service.build(query)

    def test_service_rejects_invalid_start_date(self, flour_recipe):
        """Некорректная дата начала периода приводит к ошибке."""
        flour, dish, recipe = flour_recipe
        service = osv_service(
            fake_manager([flour, dish], [recipe]),
            today=datetime.date(2026, 1, 15),
        )
        query = filter_dto("nomenclature", "name", "Мука", filter_type.LIKE)

        with pytest.raises(arguments_exception):
            service.build(query, start_date="not-a-date")

        with pytest.raises(arguments_exception):
            service.build(query, start_date=datetime.date(2026, 1, 20))


class TestOsvApi:
    """Интеграционные тесты POST-формирования ОСВ."""

    @pytest.fixture
    def client(self):
        """Клиент Flask для проверки POST-формирования ОСВ."""
        main.app.config["TESTING"] = True
        with main.app.test_client() as client:
            yield client

    def test_post_osv_returns_filtered_report(self, client):
        """POST /api/osv возвращает ОСВ с учетом DTO фильтрации."""
        response = client.post(
            "/api/osv",
            json={
                "field_name": "name",
                "value": "Мука",
                "filter_type": "LIKE",
            },
        )

        assert response.status_code == 200
        rows = response.get_json()

        assert [row["name"] for row in rows] == ["Мука пшеничная"]
        assert set(rows[0]) == {
            "code",
            "name",
            "unit",
            "opening_balance",
            "income",
            "outcome",
            "closing_balance",
        }

    def test_post_osv_accepts_entity_type_and_start_date(self, client):
        """Тип модели и дата начала периода передаются в теле запроса."""
        response = client.post(
            "/api/osv",
            json={
                "entity_type": "nomenclature",
                "field_name": "name",
                "value": "Молочные продукты",
                "filter_type": "EQUALS",
                "start_date": "2000-01-01",
            },
        )

        assert response.status_code == 200
        assert {row["name"] for row in response.get_json()} == {
            "Молоко 3.2%",
            "Яйца куриные",
            "Масло сливочное",
            "Творог 9%",
            "Сметана 15%",
        }

    def test_post_osv_available_by_report_alias(self, client):
        """ОСВ доступна по адресу /api/report/osv."""
        response = client.post(
            "/api/report/osv",
            json={"field_name": "name", "value": "Суп", "filter_type": "LIKE"},
        )

        assert response.status_code == 200
        assert [row["name"] for row in response.get_json()] == ["Суп-лапша домашняя"]

    def test_post_osv_rejects_foreign_entity_type(self, client):
        """ОСВ по другому типу доменной модели возвращает HTTP 400."""
        response = client.post(
            "/api/osv",
            json={
                "entity_type": "group",
                "field_name": "name",
                "value": "Бакалея",
                "filter_type": "EQUALS",
            },
        )

        assert response.status_code == 400

    def test_post_osv_rejects_invalid_filter(self, client):
        """Некорректный вариант фильтрации возвращает HTTP 400."""
        response = client.post(
            "/api/osv",
            json={
                "field_name": "name",
                "value": "Мука",
                "filter_type": "UNKNOWN",
            },
        )

        assert response.status_code == 400

    def test_post_osv_rejects_invalid_start_date(self, client):
        """Некорректная дата начала периода возвращает HTTP 400."""
        response = client.post(
            "/api/osv",
            json={
                "field_name": "name",
                "value": "Мука",
                "filter_type": "LIKE",
                "start_date": "not-a-date",
            },
        )

        assert response.status_code == 400
