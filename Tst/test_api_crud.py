import uuid

import pytest

import main


COLLECTIONS = ("storages", "ranges", "nomenclatures", "groups", "recipes")


@pytest.fixture(autouse=True)
def restore_storage():
    """Восстанавливает содержимое хранилища после каждого интеграционного теста."""

    snapshot = {
        name: dict(getattr(main.storage, name))
        for name in COLLECTIONS
    }

    yield

    for name, items in snapshot.items():
        collection = getattr(main.storage, name)
        collection.clear()
        collection.update(items)


@pytest.fixture
def client():
    main.app.config["TESTING"] = True
    with main.app.test_client() as client:
        yield client


@pytest.fixture
def existing_group_id():
    return str(next(iter(main.storage.groups.values())).id)


@pytest.fixture
def existing_range_id():
    return str(next(iter(main.storage.ranges.values())).id)


def create_entity(client, entity_type, payload):
    return client.post(f"/api/entities/{entity_type}", json=payload)



class TestReportFormats:
    """GET /api/formats — список форматов для построения отчетов."""

    def test_formats_returns_json_list(self, client):
        response = client.get("/api/formats")

        assert response.status_code == 200
        assert response.is_json

        formats = response.get_json()
        assert isinstance(formats, list)
        assert formats == ["txt", "csv", "markdown", "xml", "html"]

    def test_formats_alias(self, client):
        response = client.get("/api/get_formats")

        assert response.status_code == 200
        assert response.get_json() == ["txt", "csv", "markdown", "xml", "html"]

    def test_format_details_contains_delivery_metadata(self, client):
        response = client.get("/api/formats/details")

        assert response.status_code == 200

        details = {item["name"]: item for item in response.get_json()}
        assert details["csv"]["mimetype"] == "text/csv"
        assert details["csv"]["extension"] == "csv"
        assert details["csv"]["download"] is True
        assert details["html"]["mimetype"] == "text/html"
        assert details["html"]["download"] is False




class TestGroupCrud:
    """CRUD для групп номенклатуры."""

    def test_create_read_update_delete_group(self, client):
        created = create_entity(client, "group", {"name": "Тестовая группа"})

        assert created.status_code == 200
        group = created.get_json()
        group_id = group["id"]
        assert group["name"] == "Тестовая группа"
        assert group["$type"] == "nomenclature_group_model"

        found = client.get(f"/api/entities/group/{group_id}")
        assert found.status_code == 200
        assert found.get_json()["name"] == "Тестовая группа"

        updated = client.put(
            f"/api/entities/group/{group_id}",
            json={"name": "Измененная группа"},
        )
        assert updated.status_code == 200
        assert updated.get_json()["name"] == "Измененная группа"

        listed = client.get("/api/entities/group")
        assert listed.status_code == 200
        assert group_id in [item["id"] for item in listed.get_json()]

        deleted = client.delete(f"/api/entities/group/{group_id}")
        assert deleted.status_code == 200
        assert deleted.get_json()["id"] == group_id
        assert deleted.get_json()["deleted"] is True

        assert client.get(f"/api/entities/group/{group_id}").status_code == 404


class TestStorageCrud:
    """CRUD для складов."""

    def test_storage_crud(self, client):
        created = create_entity(
            client,
            "storage",
            {"name": "Тестовый склад", "address": "ул. Тестовая, 1"},
        )

        assert created.status_code == 200
        storage_id = created.get_json()["id"]

        updated = client.patch(
            f"/api/entities/storage/{storage_id}",
            json={"address": "ул. Новая, 2"},
        )
        assert updated.status_code == 200
        assert updated.get_json()["address"] == "ул. Новая, 2"
        assert updated.get_json()["name"] == "Тестовый склад"

        assert client.delete(f"/api/entities/storage/{storage_id}").status_code == 200


class TestNomenclatureCrud:
    """CRUD для номенклатуры со ссылками на группу и единицу измерения."""

    def test_nomenclature_crud(self, client, existing_group_id, existing_range_id):
        created = create_entity(
            client,
            "nomenclature",
            {
                "name": "Тестовая номенклатура",
                "full_name": "Тестовая номенклатура полное наименование",
                "group": existing_group_id,
                "range": existing_range_id,
            },
        )

        assert created.status_code == 200
        item = created.get_json()
        item_id = item["id"]
        assert item["group"]["id"] == existing_group_id
        assert item["range"]["id"] == existing_range_id

        updated = client.put(
            f"/api/entities/nomenclature/{item_id}",
            json={"full_name": "Новое полное наименование"},
        )
        assert updated.status_code == 200
        assert updated.get_json()["full_name"] == "Новое полное наименование"
        assert updated.get_json()["group"]["id"] == existing_group_id
        assert updated.get_json()["range"]["id"] == existing_range_id

        assert client.delete(f"/api/entities/nomenclature/{item_id}").status_code == 200


class TestRecipeCrud:
    """CRUD для рецептов с вложенными позициями."""

    def test_recipe_crud_with_items(self, client, existing_range_id):
        created = create_entity(
            client,
            "recipe",
            {
                "name": "Тестовый рецепт",
                "description": "Описание тестового рецепта",
                "items": [
                    {
                        "name": "Мука",
                        "weight": 100,
                        "range": existing_range_id,
                        "type": "ingredient",
                    }
                ],
            },
        )

        assert created.status_code == 200
        recipe = created.get_json()
        recipe_id = recipe["id"]
        assert len(recipe["items"]) == 1
        assert recipe["items"][0]["range"]["id"] == existing_range_id

        updated = client.put(
            f"/api/entities/recipe/{recipe_id}",
            json={"description": "Новое описание"},
        )
        assert updated.status_code == 200
        assert updated.get_json()["description"] == "Новое описание"
        assert len(updated.get_json()["items"]) == 1

        assert client.delete(f"/api/entities/recipe/{recipe_id}").status_code == 200



class TestEntityRelations:
    """Запрет удаления и смены кода связанных сущностей."""

    def test_cannot_delete_linked_group_and_range(
        self, client, existing_group_id, existing_range_id
    ):
        group = create_entity(client, "group", {"name": "Связанная группа"}).get_json()
        range_item = create_entity(
            client, "range", {"name": "связанная единица", "conversion_factor": 1}
        ).get_json()

        nomenclature = create_entity(
            client,
            "nomenclature",
            {
                "name": "Связанная номенклатура",
                "full_name": "Связанная номенклатура полное",
                "group": group["id"],
                "range": range_item["id"],
            },
        ).get_json()

        deleted_group = client.delete(f"/api/entities/group/{group['id']}")
        assert deleted_group.status_code == 400
        assert "связана" in deleted_group.get_json()["error"]

        deleted_range = client.delete(f"/api/entities/range/{range_item['id']}")
        assert deleted_range.status_code == 400
        assert "связана" in deleted_range.get_json()["error"]

        # Удаление номенклатуры освобождает связи
        assert client.delete(
            f"/api/entities/nomenclature/{nomenclature['id']}"
        ).status_code == 200
        assert client.delete(f"/api/entities/group/{group['id']}").status_code == 200
        assert client.delete(f"/api/entities/range/{range_item['id']}").status_code == 200

    def test_cannot_change_code_of_linked_entity(self, client):
        group = create_entity(client, "group", {"name": "Группа с кодом"}).get_json()
        range_item = create_entity(
            client, "range", {"name": "единица с кодом", "conversion_factor": 1}
        ).get_json()

        create_entity(
            client,
            "nomenclature",
            {
                "name": "Номенклатура с кодом",
                "full_name": "Номенклатура с кодом полное",
                "group": group["id"],
                "range": range_item["id"],
            },
        )

        new_code = str(uuid.uuid4())
        response = client.put(
            f"/api/entities/group/{group['id']}",
            json={"id": new_code},
        )

        assert response.status_code == 400
        assert "код" in response.get_json()["error"]

    def test_can_change_name_of_linked_entity(self, client, existing_range_id):
        group = create_entity(client, "group", {"name": "Группа для переименования"}).get_json()

        create_entity(
            client,
            "nomenclature",
            {
                "name": "Номенклатура для переименования",
                "full_name": "Номенклатура для переименования полное",
                "group": group["id"],
                "range": existing_range_id,
            },
        )

        response = client.patch(
            f"/api/entities/group/{group['id']}",
            json={"name": "Переименованная группа"},
        )

        assert response.status_code == 200
        assert response.get_json()["name"] == "Переименованная группа"

    def test_cannot_delete_base_range(self, client):
        base = create_entity(
            client, "range", {"name": "базовая единица", "conversion_factor": 1}
        ).get_json()

        derived = create_entity(
            client,
            "range",
            {
                "name": "производная единица",
                "conversion_factor": 1000,
                "base_range": base["id"],
            },
        ).get_json()

        response = client.delete(f"/api/entities/range/{base['id']}")
        assert response.status_code == 400
        assert "связана" in response.get_json()["error"]

        assert client.delete(f"/api/entities/range/{derived['id']}").status_code == 200
        assert client.delete(f"/api/entities/range/{base['id']}").status_code == 200

    def test_range_cycle_is_rejected(self, client):
        first = create_entity(
            client, "range", {"name": "первая единица", "conversion_factor": 1}
        ).get_json()

        second = create_entity(
            client,
            "range",
            {
                "name": "вторая единица",
                "conversion_factor": 2,
                "base_range": first["id"],
            },
        ).get_json()

        response = client.put(
            f"/api/entities/range/{first['id']}",
            json={"base_range": second["id"]},
        )

        assert response.status_code == 400
        assert "циклическая" in response.get_json()["error"]



class TestCrudErrors:
    """Проверка ошибок и валидации запросов."""

    def test_unsupported_entity_type(self, client):
        response = client.get("/api/entities/ingredient")

        assert response.status_code == 400
        assert "Неподдерживаемый тип" in response.get_json()["error"]

    def test_not_found_get_update_delete(self, client):
        missing_code = str(uuid.uuid4())

        assert client.get(f"/api/entities/group/{missing_code}").status_code == 404
        assert client.put(
            f"/api/entities/group/{missing_code}", json={"name": "x"}
        ).status_code == 404
        assert client.delete(f"/api/entities/group/{missing_code}").status_code == 404

    def test_create_invalid_payload(self, client, existing_range_id):
        missing_full_name = create_entity(
            client,
            "nomenclature",
            {"name": "Без полного имени", "range": existing_range_id},
        )
        assert missing_full_name.status_code == 400

        missing_group = create_entity(
            client,
            "nomenclature",
            {
                "name": "Без группы",
                "full_name": "Без группы полное",
                "range": existing_range_id,
            },
        )
        assert missing_group.status_code == 400

        missing_reference = create_entity(
            client,
            "nomenclature",
            {
                "name": "Несуществующая группа",
                "full_name": "Несуществующая группа полное",
                "group": str(uuid.uuid4()),
                "range": existing_range_id,
            },
        )
        assert missing_reference.status_code == 400

    def test_create_without_json_body(self, client):
        response = client.post("/api/entities/group", data="not-json")

        assert response.status_code == 400

    def test_duplicate_code_is_rejected(self, client):
        group = create_entity(client, "group", {"name": "Первая группа"}).get_json()

        response = create_entity(
            client,
            "group",
            {"id": group["id"], "name": "Вторая группа"},
        )

        assert response.status_code == 400
        assert "уже существует" in response.get_json()["error"]


class TestSwagger:
    """Проверка подключения Swagger и доступности спецификации."""

    def test_openapi_yaml_is_available(self, client):
        response = client.get("/openapi.yaml")

        assert response.status_code == 200
        content = response.get_data(as_text=True)
        assert "openapi: 3.0.3" in content
        assert "/api/entities/{entity_type}" in content

    def test_openapi_yaml_alias(self, client):
        response = client.get("/api/openapi.yaml")

        assert response.status_code == 200
        assert "openapi" in response.get_data(as_text=True)

    def test_swagger_ui_is_available(self, client):
        response = client.get("/api/docs/")

        assert response.status_code == 200
        assert "swagger" in response.get_data(as_text=True).lower()
