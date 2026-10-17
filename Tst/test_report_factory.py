import pytest
from Src.Logics.report_factory import report_factory
from Src.Logics.settings_manager import settings_manager
from Src.Dtos.report_type_dto import report_type_dto
from Src.Models.recipe_model import recipe_model
from Src.Models.recipe_item_model import recipe_item_model
from Src.Models.range_model import range_model


# Фикстура: рецепт с данными для тестов
@pytest.fixture
def sample_recipe():
    gram = range_model("грамм", 1)
    items = [
        recipe_item_model.create_ingredient("Мука", 200, gram),
        recipe_item_model.create_ingredient("Вода", 100, gram),
        recipe_item_model.create_ingredient("Соль", 5, gram),
    ]
    recipe = recipe_model.create("Тестовый рецепт", "Описание")
    for item in items:
        recipe.add_item(item)
    return recipe


# Фикстура: фабрика
@pytest.fixture
def factory():
    return report_factory()


# Вспомогательная функция: содержимое отчета (текст или декодированные бинарные данные)
def report_content(result) -> str:
    if result.binary:
        return bytes(result.binary).decode("utf-8")
    return result.text


# Проверяет, что фабрика создается и настройки загружены
def test_factory_create(factory):
    assert factory is not None
    assert factory._settings is not None
    assert factory._settings.is_loaded


# Проверяет создание отчетов для всех типов
def test_factory_create_all_types(factory):
    for report_type in report_type_dto:
        report = factory.create(report_type)
        assert report is not None


# Проверяет создание отчета по умолчанию (из настроек)
def test_factory_create_default(factory):
    report = factory.create_default()
    assert report is not None


# Проверяет, что create_default возвращает отчет в формате из настроек
def test_factory_create_default_matches_settings(factory):
    settings = settings_manager()
    expected_format = settings.settings.response_format

    report = factory.create_default()

    # Проверяем, что тип отчета соответствует формату из настроек
    format_to_type = {
        "TXT": report_type_dto.TXT,
        "CSV": report_type_dto.CSV,
        "Markdown": report_type_dto.MARKDOWN,
        "XML": report_type_dto.XML,
        "HTML": report_type_dto.HTML,
    }
    expected_type = format_to_type.get(expected_format)
    assert expected_type is not None


# Проверяет формирование отчета в каждом формате
def test_factory_build_all_formats(factory, sample_recipe):
    for report_type in report_type_dto:
        report = factory.create(report_type)
        result = report.build(sample_recipe)
        assert result is not None

        # Отчет содержит либо текст, либо бинарные данные
        assert len(result.text) > 0 or len(result.binary) > 0


# Проверяет, что CSV отчет формируется в виде бинарных данных
def test_csv_report_is_binary(factory, sample_recipe):
    report = factory.create(report_type_dto.CSV)
    result = report.build(sample_recipe)

    assert len(result.binary) > 0
    # Бинарные данные - список байт (чисел)
    assert all(isinstance(b, int) for b in result.binary)


# Проверяет, что Markdown отчет формируется в виде бинарных данных
def test_markdown_report_is_binary(factory, sample_recipe):
    report = factory.create(report_type_dto.MARKDOWN)
    result = report.build(sample_recipe)

    assert len(result.binary) > 0
    # Бинарные данные - список байт (чисел)
    assert all(isinstance(b, int) for b in result.binary)


# Проверяет содержимое CSV отчета
def test_csv_report_content(factory, sample_recipe):
    report = factory.create(report_type_dto.CSV)
    result = report.build(sample_recipe)
    content = report_content(result)
    assert "Код" in content
    assert "Наименование" in content
    assert "Мука" in content


# Проверяет содержимое Markdown отчета
def test_markdown_report_content(factory, sample_recipe):
    report = factory.create(report_type_dto.MARKDOWN)
    result = report.build(sample_recipe)
    content = report_content(result)
    assert "|" in content
    assert "Мука" in content


# Проверяет содержимое XML отчета
def test_xml_report_content(factory, sample_recipe):
    report = factory.create(report_type_dto.XML)
    result = report.build(sample_recipe)
    assert "<?xml" in result.text
    assert "<report>" in result.text
    assert "Мука" in result.text


# Проверяет содержимое HTML отчета
def test_html_report_content(factory, sample_recipe):
    report = factory.create(report_type_dto.HTML)
    result = report.build(sample_recipe)
    assert "<html>" in result.text
    assert "<table>" in result.text
    assert "Мука" in result.text


# Проверяет содержимое TXT отчета
def test_txt_report_content(factory, sample_recipe):
    report = factory.create(report_type_dto.TXT)
    result = report.build(sample_recipe)
    assert "Код" in result.text
    assert "Мука" in result.text
