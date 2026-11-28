import json

import pytest

import main
from Src.Core.abstract_observer import abstract_observer
from Src.Core.log_type import log_category, log_operation, log_status
from Src.Dtos.log_event_dto import log_event_dto
from Src.Logics.file_log_observer import file_log_observer
from Src.Logics.logging_service import logging_service
from Src.Logics.memory_log_observer import memory_log_observer
from Src.Logics.settings_manager import settings_manager


COLLECTIONS = ("storages", "ranges", "nomenclatures", "groups", "recipes")


class spy_observer(abstract_observer):
    """сохраняет события для проверки в тестах"""

    def __init__(self):
        self.events = []

    def update(self, event):
        self.events.append(event)


@pytest.fixture(autouse=True)
def restore_storage():
    """Восстанавливает содержимое хранилища после каждого теста."""

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
    """Клиент Flask для интеграционных тестов."""

    main.app.config["TESTING"] = True
    with main.app.test_client() as client:
        yield client


@pytest.fixture
def audit_spy():
    """Подписывает наблюдателя на общий журнал приложения."""

    service = logging_service()
    spy = spy_observer()
    service.attach(spy)

    yield spy

    service.detach(spy)


def has_event(spy, category, operation, entity_type=None):
    """Проверяет наличие события с указанными категорией и операцией."""

    for event in spy.events:
        if event.category != category.value:
            continue

        if event.operation != operation.value:
            continue

        if entity_type is not None and event.entity_type != entity_type:
            continue

        return True

    return False


class TestObserverPattern:
    """Проверка контракта шаблона «Наблюдатель»."""

    def test_attach_detach_and_notify(self):
        service = logging_service()
        spy = spy_observer()

        service.attach(spy)
        service.log(log_event_dto(
            category=log_category.CRUD,
            operation=log_operation.READ,
            message="тестовое событие",
        ))

        assert len(spy.events) == 1
        assert spy.events[0].message == "тестовое событие"

        service.detach(spy)
        service.log(log_event_dto(
            category=log_category.CRUD,
            operation=log_operation.READ,
            message="событие после отписки",
        ))

        assert len(spy.events) == 1

    def test_observer_errors_do_not_break_notify(self):
        service = logging_service()

        class broken_observer(abstract_observer):
            def update(self, event):
                raise RuntimeError("сбой наблюдателя")

        spy = spy_observer()
        service.attach(broken_observer())
        service.attach(spy)

        try:
            service.log(log_event_dto(message="событие при сбое наблюдателя"))
        finally:
            service.detach(service.observers[-2])

        assert len(spy.events) >= 1
        service.detach(spy)


class TestAuditObservers:
    """Проверка конкретных наблюдателей."""

    def test_file_observer_writes_json_array(self, tmp_path):
        log_file = tmp_path / "audit.json"
        observer = file_log_observer(str(log_file))

        observer.update(log_event_dto(
            category=log_category.CRUD,
            operation=log_operation.CREATE,
            message="создана сущность",
            details={"name": "Тест"},
        ))
        observer.update(log_event_dto(
            category=log_category.WAREHOUSE,
            operation=log_operation.REPORT,
            message="сформирована ОСВ",
        ))

        events = json.loads(log_file.read_text(encoding="utf-8"))
        assert isinstance(events, list)
        assert len(events) == 2

        assert events[0]["category"] == "CRUD"
        assert events[0]["operation"] == "CREATE"
        assert events[0]["message"] == "создана сущность"
        assert events[0]["details"]["name"] == "Тест"
        assert events[1]["category"] == "WAREHOUSE"

    def test_memory_observer_keeps_only_capacity(self):
        observer = memory_log_observer(capacity=2)

        for index in range(3):
            observer.update(log_event_dto(message=str(index)))

        assert len(observer.events) == 2
        assert [event.message for event in observer.events] == ["1", "2"]

    def test_event_is_json_safe(self):
        import datetime
        import uuid

        event = log_event_dto(
            details={
                "id": uuid.uuid4(),
                "date": datetime.date(2026, 1, 1),
            }
        )

        payload = event.to_dict()
        assert isinstance(payload["details"]["id"], str)
        assert payload["details"]["date"] == "2026-01-01"


class TestCrudLogging:
    """CRUD-операции должны попадать в журнал."""

    def test_create_read_update_delete_group_are_logged(self, client, audit_spy):
        created = client.post(
            "/api/entities/group",
            json={"name": "Группа для журнала"},
        )
        assert created.status_code == 200
        group_id = created.get_json()["id"]

        assert client.get(f"/api/entities/group/{group_id}").status_code == 200
        assert client.put(
            f"/api/entities/group/{group_id}",
            json={"name": "Группа для журнала 2"},
        ).status_code == 200
        assert client.delete(f"/api/entities/group/{group_id}").status_code == 200

        for operation in (
            log_operation.CREATE,
            log_operation.READ,
            log_operation.UPDATE,
            log_operation.DELETE,
        ):
            assert has_event(audit_spy, log_category.CRUD, operation, "group")

    def test_failed_crud_operation_is_logged(self, client, audit_spy):
        response = client.post(
            "/api/entities/group",
            json={"name": ""},
        )

        assert response.status_code == 400
        assert any(
            event.category == log_category.CRUD.value
            and event.operation == log_operation.CREATE.value
            and event.status == log_status.FAILURE.value
            for event in audit_spy.events
        )


class TestWarehouseLogging:
    """Складские операции должны попадать в журнал категорией WAREHOUSE."""

    def test_storage_crud_is_logged_as_warehouse(self, client, audit_spy):
        created = client.post(
            "/api/entities/storage",
            json={"name": "Склад для журнала", "address": "ул. Тестовая, 1"},
        )
        assert created.status_code == 200
        storage_id = created.get_json()["id"]

        assert client.delete(f"/api/entities/storage/{storage_id}").status_code == 200

        assert has_event(
            audit_spy,
            log_category.WAREHOUSE,
            log_operation.CREATE,
            "storage",
        )
        assert has_event(
            audit_spy,
            log_category.WAREHOUSE,
            log_operation.DELETE,
            "storage",
        )

    def test_osv_is_logged_as_warehouse_report(self, client, audit_spy):
        response = client.post(
            "/api/osv",
            json={
                "entity_type": "nomenclature",
                "field_name": "name",
                "value": "Мука",
                "filter_type": "LIKE",
            },
        )

        assert response.status_code == 200
        assert has_event(
            audit_spy,
            log_category.WAREHOUSE,
            log_operation.REPORT,
            "nomenclature",
        )


class TestWebLogging:
    """Вызовы Web-методов должны попадать в журнал."""

    def test_web_call_is_logged(self, client, audit_spy):
        response = client.get("/api/formats")
        assert response.status_code == 200

        web_events = [
            event for event in audit_spy.events
            if event.category == log_category.WEB.value
        ]

        assert web_events
        assert web_events[-1].operation == log_operation.CALL.value
        assert web_events[-1].details["method"] == "GET"
        assert web_events[-1].details["path"] == "/api/formats"
        assert web_events[-1].details["status_code"] == 200


class TestSettingsLogging:
    """Изменение параметров настроек должно попадать в журнал."""

    def test_settings_change_is_logged(self, client, audit_spy):
        manager = settings_manager()
        manager.load()
        previous_format = manager.settings.response_format

        try:
            response = client.patch(
                "/api/settings",
                json={"response_format": "CSV"},
            )

            assert response.status_code == 200
            assert response.get_json()["response_format"] == "CSV"

            settings_events = [
                event for event in audit_spy.events
                if event.category == log_category.SETTINGS.value
                and event.operation == log_operation.UPDATE.value
            ]

            assert settings_events
            details = settings_events[-1].details
            assert details["before"]["response_format"] == previous_format
            assert details["after"]["response_format"] == "CSV"
        finally:
            manager.settings.response_format = previous_format

    def test_invalid_settings_change_is_rejected(self, client, audit_spy):
        response = client.patch(
            "/api/settings",
            json={"response_format": "JSON"},
        )

        assert response.status_code == 400
        assert any(
            event.category == log_category.SETTINGS.value
            and event.operation == log_operation.UPDATE.value
            and event.status == log_status.FAILURE.value
            for event in audit_spy.events
        )

    def test_unknown_settings_parameter_is_rejected(self, client):
        response = client.patch(
            "/api/settings",
            json={"unknown_parameter": 1},
        )

        assert response.status_code == 400


class TestAuditLogApi:
    """API журнала аудита."""

    def test_logs_endpoint_returns_events(self, client):
        client.get("/api/formats")

        response = client.get("/api/logs?category=WEB&limit=10")

        assert response.status_code == 200
        events = response.get_json()
        assert isinstance(events, list)
        assert all(event["category"] == "WEB" for event in events)

    def test_logs_endpoint_validates_limit(self, client):
        assert client.get("/api/logs?limit=abc").status_code == 400
        assert client.get("/api/logs?limit=-1").status_code == 400
