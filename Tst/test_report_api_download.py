import pytest
import main


# Фикстура: HTTP клиент Flask приложения
@pytest.fixture
def client():
    main.app.config["TESTING"] = True
    with main.app.test_client() as client:
        yield client


# Фикстура: код (UUID) первого рецепта из хранилища первого старта
@pytest.fixture
def recipe_id():
    assert len(main.storage.recipes) > 0
    return str(next(iter(main.storage.recipes.values())).id)


# ============================================================
# Тесты скачивания бинарных отчетов (CSV, Markdown)
# ============================================================

class TestBinaryDownload:
    """Тесты: CSV и Markdown формируются в бинарных данных и скачиваются файлом"""

    def test_csv_report_is_downloaded_as_file(self, client, recipe_id):
        """CSV отчет отдается скачиванием файла"""
        response = client.get(f"/api/report/recipe/{recipe_id}/csv")

        assert response.status_code == 200

        disposition = response.headers.get("Content-Disposition", "")
        assert disposition.startswith("attachment")
        assert f"recipe_{recipe_id}.csv" in disposition

        assert response.mimetype == "text/csv"

    def test_csv_report_binary_content(self, client, recipe_id):
        """CSV отчет содержит бинарные данные (байты) с корректным содержимым"""
        response = client.get(f"/api/report/recipe/{recipe_id}/csv")

        data = response.get_data()
        assert isinstance(data, bytes)
        assert len(data) > 0

        content = data.decode("utf-8")
        assert "Код" in content
        assert "Наименование" in content

    def test_markdown_report_is_downloaded_as_file(self, client, recipe_id):
        """Markdown отчет отдается скачиванием файла"""
        response = client.get(f"/api/report/recipe/{recipe_id}/markdown")

        assert response.status_code == 200

        disposition = response.headers.get("Content-Disposition", "")
        assert disposition.startswith("attachment")
        assert f"recipe_{recipe_id}.md" in disposition

        assert response.mimetype == "text/markdown"

    def test_markdown_report_binary_content(self, client, recipe_id):
        """Markdown отчет содержит бинарные данные (байты) с корректным содержимым"""
        response = client.get(f"/api/report/recipe/{recipe_id}/markdown")

        data = response.get_data()
        assert isinstance(data, bytes)
        assert len(data) > 0

        content = data.decode("utf-8")
        assert "|" in content


# ============================================================
# Тесты структурированного текста для остальных форматов
# ============================================================

class TestStructuredText:
    """Тесты: остальные форматы возвращаются структурированным текстом"""

    def test_txt_report_returns_structured_text(self, client, recipe_id):
        """TXT отчет возвращается текстом без скачивания"""
        response = client.get(f"/api/report/recipe/{recipe_id}/txt")

        assert response.status_code == 200
        assert "Content-Disposition" not in response.headers
        assert response.mimetype == "text/plain"
        assert "Код" in response.get_data(as_text=True)

    def test_universal_format_removed(self, client, recipe_id):
        """Формат universal больше не поддерживается - ошибка 400"""
        response = client.get(f"/api/report/recipe/{recipe_id}/universal")

        assert response.status_code == 400
        assert "Неподдерживаемый формат отчета" in response.get_data(as_text=True)

    def test_xml_report_returns_structured_text(self, client, recipe_id):
        """XML отчет возвращается текстом без скачивания"""
        response = client.get(f"/api/report/recipe/{recipe_id}/xml")

        assert response.status_code == 200
        assert "Content-Disposition" not in response.headers
        assert response.mimetype == "application/xml"
        assert "<?xml" in response.get_data(as_text=True)

    def test_html_report_returns_structured_text(self, client, recipe_id):
        """HTML отчет возвращается текстом без скачивания"""
        response = client.get(f"/api/report/recipe/{recipe_id}/html")

        assert response.status_code == 200
        assert "Content-Disposition" not in response.headers
        assert response.mimetype == "text/html"
        assert "<html>" in response.get_data(as_text=True)


# ============================================================
# Тесты отчета в формате из настроек (create_default)
# ============================================================

class TestReportBySettings:
    """Тесты: отчет для типа и кода сущности в формате из настроек приложения (create_default)"""

    def test_report_by_settings_uses_response_format(self, client, recipe_id):
        """Формат отчета определяется настройками приложения (response_format)"""
        response = client.get(f"/api/report_default/recipe/{recipe_id}")

        assert response.status_code == 200

        expected_mimetype = {
            "TXT": "text/plain",
            "TEXT": "text/plain",
            "CSV": "text/csv",
            "Markdown": "text/markdown",
            "XML": "application/xml",
            "HTML": "text/html",
        }[main.settings.settings.response_format]
        assert response.mimetype == expected_mimetype

    def test_report_by_settings_text_format(self, client, recipe_id):
        """Текстовые форматы из настроек возвращаются структурированным текстом"""
        original = main.settings.settings.response_format
        try:
            main.settings.settings.response_format = "TXT"
            response = client.get(f"/api/report_default/recipe/{recipe_id}")
        finally:
            main.settings.settings.response_format = original

        assert response.status_code == 200
        assert "Content-Disposition" not in response.headers
        assert "Код" in response.get_data(as_text=True)

    def test_report_by_settings_binary_format_downloads_file(self, client, recipe_id):
        """CSV в настройках - отчет отдается скачиванием бинарного файла"""
        original = main.settings.settings.response_format
        try:
            main.settings.settings.response_format = "CSV"
            response = client.get(f"/api/report_default/recipe/{recipe_id}")
        finally:
            main.settings.settings.response_format = original

        assert response.status_code == 200

        disposition = response.headers.get("Content-Disposition", "")
        assert disposition.startswith("attachment")
        assert f"recipe_{recipe_id}.csv" in disposition

        content = response.get_data().decode("utf-8")
        assert "Код" in content

    def test_report_by_settings_nomenclature(self, client):
        """Эндпоинт работает для типа сущности nomenclature"""
        nomenclature_id = str(next(iter(main.storage.nomenclatures.values())).id)

        response = client.get(f"/api/report_default/nomenclature/{nomenclature_id}")

        assert response.status_code == 200
        assert len(response.get_data()) > 0

    def test_report_by_settings_range(self, client):
        """Эндпоинт работает для типа сущности range"""
        range_id = str(next(iter(main.storage.ranges.values())).id)

        response = client.get(f"/api/report_default/range/{range_id}")

        assert response.status_code == 200
        assert len(response.get_data()) > 0

    def test_report_by_settings_invalid_entity_type(self, client, recipe_id):
        """Неподдерживаемый тип сущности - ошибка 400"""
        response = client.get(f"/api/report_default/ingredient/{recipe_id}")

        assert response.status_code == 400
        assert "Неподдерживаемый тип сущности" in response.get_data(as_text=True)

    def test_report_by_settings_not_found(self, client):
        """Неверный код сущности - ошибка 404"""
        response = client.get("/api/report_default/recipe/00000000-0000-0000-0000-000000000000")

        assert response.status_code == 404
        assert "не найдена" in response.get_data(as_text=True)
