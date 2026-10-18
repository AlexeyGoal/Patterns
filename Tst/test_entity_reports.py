import pytest
from Src.Core.exception import arguments_exception
from Src.Logics.report_factory import report_factory
from Src.Logics.report_source_builder import report_source_builder
from Src.Logics.storage_manager import storage_manager
from Src.Dtos.report_type_dto import report_type_dto


# Фикстура: фабрика
@pytest.fixture
def factory():
    return report_factory()


# Фикстура: хранилище (данные первого старта)
@pytest.fixture
def storage():
    manager = storage_manager()
    manager.convert()
    return manager


# Вспомогательная функция: содержимое отчета (текст или декодированные бинарные данные)
def report_content(result) -> str:
    if result.binary:
        return bytes(result.binary).decode("utf-8")
    return result.text


# Форматы, которые обязаны поддерживать все типы сущностей
ALL_FORMATS = [
    report_type_dto.TXT,
    report_type_dto.CSV,
    report_type_dto.MARKDOWN,
    report_type_dto.XML,
    report_type_dto.HTML,
]


# ============================================================
# Тесты отчета по номенклатуре
# ============================================================

class TestNomenclatureReport:
    """Тесты формирования отчета по номенклатуре во всех форматах"""

    @pytest.fixture
    def nomenclature(self, storage):
        assert len(storage.nomenclatures) > 0
        return next(iter(storage.nomenclatures.values()))

    def test_all_formats_build_without_errors(self, factory, nomenclature):
        """Отчет строится во всех форматах без ошибок"""
        for report_type in ALL_FORMATS:
            report = factory.create(report_type)
            result = report.build(nomenclature)

            assert len(report_content(result)) > 0, f"Пустой отчет в формате {report_type}"

    def test_all_formats_contain_name(self, factory, nomenclature):
        """Наименование присутствует во всех форматах"""
        for report_type in ALL_FORMATS:
            report = factory.create(report_type)
            content = report_content(report.build(nomenclature))

            assert nomenclature.name in content, f"Нет наименования в формате {report_type}"

    def test_all_formats_contain_full_name(self, factory, nomenclature):
        """Полное наименование присутствует во всех форматах"""
        for report_type in ALL_FORMATS:
            report = factory.create(report_type)
            content = report_content(report.build(nomenclature))

            assert nomenclature.full_name in content, f"Нет полного наименования в формате {report_type}"

    def test_text_format_is_table(self, factory, nomenclature):
        """TXT формат - таблица с заголовками колонок"""
        report = factory.create(report_type_dto.TXT)
        content = report_content(report.build(nomenclature))

        assert "Код | Наименование | Полное наименование | Группа | Единица измерения" in content

    def test_csv_format_is_binary_with_header(self, factory, nomenclature):
        """CSV формат - бинарные данные с заголовком колонок"""
        report = factory.create(report_type_dto.CSV)
        result = report.build(nomenclature)

        assert len(result.binary) > 0
        content = report_content(result)
        assert "Код;Наименование;Полное наименование;Группа;Единица измерения" in content

    def test_markdown_format_is_binary_table(self, factory, nomenclature):
        """Markdown формат - бинарные данные с таблицей"""
        report = factory.create(report_type_dto.MARKDOWN)
        result = report.build(nomenclature)

        assert len(result.binary) > 0
        content = report_content(result)
        assert "| Код | Наименование | Полное наименование | Группа | Единица измерения |" in content

    def test_xml_format_has_items_elements(self, factory, nomenclature):
        """XML формат содержит элементы items/item"""
        report = factory.create(report_type_dto.XML)
        content = report_content(report.build(nomenclature))

        assert '<?xml version="1.0" encoding="UTF-8"?>' in content
        assert "<report>" in content
        assert "<items>" in content
        assert "<code>" in content

    def test_html_format_has_table(self, factory, nomenclature):
        """HTML формат содержит таблицу с колонками номенклатуры"""
        report = factory.create(report_type_dto.HTML)
        content = report_content(report.build(nomenclature))

        assert "<!DOCTYPE html>" in content
        assert "<th>Код</th>" in content
        assert "<th>Наименование</th>" in content


# ============================================================
# Тесты отчета по единице измерения
# ============================================================

class TestRangeReport:
    """Тесты формирования отчета по единице измерения во всех форматах"""

    @pytest.fixture
    def range_item(self, storage):
        assert len(storage.ranges) > 0
        return next(iter(storage.ranges.values()))

    def test_all_formats_build_without_errors(self, factory, range_item):
        """Отчет строится во всех форматах без ошибок"""
        for report_type in ALL_FORMATS:
            report = factory.create(report_type)
            result = report.build(range_item)

            assert len(report_content(result)) > 0, f"Пустой отчет в формате {report_type}"

    def test_all_formats_contain_name(self, factory, range_item):
        """Наименование присутствует во всех форматах"""
        for report_type in ALL_FORMATS:
            report = factory.create(report_type)
            content = report_content(report.build(range_item))

            assert range_item.name in content, f"Нет наименования в формате {report_type}"

    def test_all_formats_contain_conversion_factor(self, factory, range_item):
        """Коэффициент пересчёта присутствует во всех форматах"""
        for report_type in ALL_FORMATS:
            report = factory.create(report_type)
            content = report_content(report.build(range_item))

            assert str(range_item.conversion_factor) in content, f"Нет коэффициента в формате {report_type}"


# ============================================================
# Тесты построителя нейтральной таблицы отчета
# ============================================================

class TestReportSourceBuilder:
    """Тесты: построитель преобразует доменные сущности в нейтральную таблицу для отчетов"""

    def test_nomenclature_table(self, storage):
        """Номенклатура строится в таблицу с нужными колонками и значениями"""
        item = next(iter(storage.nomenclatures.values()))
        table = report_source_builder.build(item)

        assert [title for _, title in table.columns] == [
            "Код", "Наименование", "Полное наименование", "Группа", "Единица измерения"
        ]
        assert len(table.rows) == 1
        assert table.rows[0]["name"] == item.name
        assert table.rows[0]["full_name"] == item.full_name
        assert table.rows[0]["group"] == item.group.name
        assert table.rows[0]["unit"] == item.range.name

    def test_range_table(self, storage):
        """Единица измерения строится в таблицу с нужными колонками и значениями"""
        item = next(iter(storage.ranges.values()))
        table = report_source_builder.build(item)

        assert [title for _, title in table.columns] == [
            "Код", "Наименование", "Коэффициент", "Базовая единица"
        ]
        assert len(table.rows) == 1
        assert table.rows[0]["name"] == item.name
        assert table.rows[0]["factor"] == str(item.conversion_factor)

    def test_recipe_table(self, storage):
        """Рецепт строится в таблицу табличной части (колонки и строки)"""
        recipe = next(iter(storage.recipes.values()))
        table = report_source_builder.build(recipe)

        assert [title for _, title in table.columns] == ["Код", "Наименование", "Брутто", "Нетто"]
        assert len(table.rows) == len(recipe.items)
        assert table.rows[0]["name"] == recipe.items[0].name

    def test_unsupported_source_raises(self, storage):
        """Неподдерживаемый тип источника приводит к ошибке аргумента"""
        with pytest.raises(arguments_exception):
            report_source_builder.build(storage)
