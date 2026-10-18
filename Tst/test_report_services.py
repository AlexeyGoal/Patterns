import pytest
from Src.Logics.storage_manager import storage_manager
from Src.Logics.report_factory import report_factory
from Src.Logics.settings_manager import settings_manager
from Src.Dtos.report_type_dto import report_type_dto


# Фикстура: хранилище (данные первого старта)
@pytest.fixture
def storage():
    manager = storage_manager()
    manager.convert()
    return manager


# Фикстура: фабрика
@pytest.fixture
def factory():
    return report_factory()


# ============================================================
# Тесты поиска сущностей в хранилище
# ============================================================

class TestStorageSearch:
    """Тесты поиска сущностей по типу и коду (методы storage_manager)"""

    def test_supported_types(self, storage):
        """Поддерживаемые типы сущностей"""
        assert set(storage.supported_types) == {"recipe", "nomenclature", "range"}

    def test_supports_is_case_insensitive(self, storage):
        """Тип сущности определяется регистронезависимо"""
        assert storage.supports("recipe")
        assert storage.supports("NOMENCLATURE")
        assert storage.supports("Range")
        assert not storage.supports("ingredient")
        assert not storage.supports("storage")

    def test_find_by_type_and_code(self, storage):
        """Поиск сущности по типу и коду для всех типов"""
        sources = {
            "recipe": storage.recipes,
            "nomenclature": storage.nomenclatures,
            "range": storage.ranges,
        }

        for entity_type, source in sources.items():
            item = next(iter(source.values()))
            found = storage.find(entity_type, str(item.id))
            assert found is item, f"Сущность {entity_type} не найдена"

    def test_find_unknown_type_returns_none(self, storage):
        """Неизвестный тип сущности - None"""
        assert storage.find("ingredient", "123") is None

    def test_find_wrong_code_returns_none(self, storage):
        """Неизвестный код сущности - None"""
        assert storage.find("recipe", "00000000-0000-0000-0000-000000000000") is None

    def test_all_returns_items(self, storage):
        """Все сущности типа и пустой список для неизвестного типа"""
        assert len(storage.all("recipe")) == len(storage.recipes)
        assert len(storage.all("nomenclature")) == len(storage.nomenclatures)
        assert storage.all("unknown") == []


# ============================================================
# Тесты доставки отчетов (метаданные наследников abstract_report)
# ============================================================

class TestReportMetadata:
    """Тесты: каждый отчет сам знает свой MIME-тип, расширение и режим скачивания"""

    @pytest.mark.parametrize("report_type, mimetype, is_download, extension", [
        (report_type_dto.TXT, "text/plain", False, "txt"),
        (report_type_dto.CSV, "text/csv", True, "csv"),
        (report_type_dto.MARKDOWN, "text/markdown", True, "md"),
        (report_type_dto.XML, "application/xml", False, "xml"),
        (report_type_dto.HTML, "text/html", False, "html"),
    ])
    def test_delivery_metadata(self, factory, report_type, mimetype, is_download, extension):
        """MIME-тип, режим скачивания и расширение каждого формата"""
        report = factory.create(report_type)

        assert report.mimetype.startswith(mimetype)
        assert report.is_download is is_download
        assert report.extension == extension

    def test_download_formats_produce_binary(self, factory):
        """Форматы со скачиванием формируют бинарные данные"""
        for report_type in (report_type_dto.CSV, report_type_dto.MARKDOWN):
            assert factory.create(report_type).is_download is True

    def test_text_formats_produce_text(self, factory):
        """Форматы без скачивания формируют структурированный текст"""
        for report_type in (report_type_dto.TXT, report_type_dto.XML, report_type_dto.HTML):
            assert factory.create(report_type).is_download is False


# ============================================================
# Тесты фабрики: создание по имени формата
# ============================================================

class TestFactoryByName:
    """Тесты: create_by_name (строковое имя формата для API и настроек)"""

    def test_create_by_name(self, factory):
        """Создание отчета по имени формата"""
        assert type(factory.create_by_name("csv")).__name__ == "csv_report"
        assert type(factory.create_by_name("markdown")).__name__ == "markdown_report"

    def test_create_by_name_is_case_insensitive(self, factory):
        """Имя формата регистронезависимо (значения настроек: CSV, Markdown, XML, TXT, HTML)"""
        assert type(factory.create_by_name("CSV")).__name__ == "csv_report"
        assert type(factory.create_by_name("Markdown")).__name__ == "markdown_report"
        assert type(factory.create_by_name("TXT")).__name__ == "text_report"

    def test_create_by_name_aliases(self, factory):
        """Алиасы txt и text ведут на один отчет"""
        assert type(factory.create_by_name("txt")).__name__ == "text_report"
        assert type(factory.create_by_name("text")).__name__ == "text_report"

    def test_create_by_name_unknown_returns_none(self, factory):
        """Неизвестный формат - None"""
        assert factory.create_by_name("pdf") is None
        assert factory.create_by_name(None) is None

    def test_supported_formats(self, factory):
        """Список поддерживаемых форматов"""
        assert set(factory.supported_formats) >= {"txt", "text", "csv", "markdown", "xml", "html"}


# ============================================================
# Тесты create_default
# ============================================================

class TestFactoryCreateDefault:
    """Тесты: create_default определяет формат из настроек приложения"""

    def test_create_default_respects_settings(self):
        """create_default возвращает класс отчета, соответствующий настройке"""
        factory = report_factory()
        settings = settings_manager()
        original = settings.settings.response_format

        expected = {
            "TXT": "text_report",
            "CSV": "csv_report",
            "Markdown": "markdown_report",
            "XML": "xml_report",
            "HTML": "html_report",
        }

        try:
            for fmt, class_name in expected.items():
                settings.settings.response_format = fmt
                report = factory.create_default()
                assert type(report).__name__ == class_name, f"Для {fmt} создан {type(report).__name__}"
        finally:
            settings.settings.response_format = original
