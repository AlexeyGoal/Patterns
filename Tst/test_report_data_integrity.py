import pytest
from Src.Logics.report_factory import report_factory
from Src.Dtos.report_type_dto import report_type_dto
from Src.Models.recipe_model import recipe_model
from Src.Models.recipe_item_model import recipe_item_model, recipe_item_type
from Src.Models.range_model import range_model


# Фикстура: рецепт с различными типами позиций
@pytest.fixture
def complex_recipe():
    gram = range_model("грамм", 1)
    piece = range_model("штука", 1)

    # Полуфабрикат с вложенными ингредиентами
    noodles = recipe_item_model.create_semi_finished("Лапша домашняя", 0, gram)
    noodles.add_item(recipe_item_model.create_ingredient("Мука пшеничная", 200, gram))
    noodles.add_item(recipe_item_model.create_ingredient("Вода", 100, gram))
    noodles.add_item(recipe_item_model.create_ingredient("Яйца", 50, gram))

    # Ингредиенты
    chicken = recipe_item_model.create_ingredient("Курица (тушка)", 900, gram)
    carrot = recipe_item_model.create_ingredient("Морковь", 150, gram)
    onion = recipe_item_model.create_ingredient("Лук репчатый", 120, gram)
    salt = recipe_item_model.create_ingredient("Соль пищевая", 30, gram)
    bay_leaf = recipe_item_model.create_ingredient("Лавровый лист", 2, piece)

    # Упаковка
    packaging = recipe_item_model.create_packaging("Порционная тарелка", 400, gram)

    recipe = recipe_model.create("Суп-лапша домашняя", "Традиционный суп-лапша")
    for item in [chicken, carrot, onion, salt, bay_leaf, noodles, packaging]:
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


# Фикстура: все позиции рецепта (включая вложенные)
def get_all_items(recipe):
    """Рекурсивно получить все позиции рецепта"""
    items = []
    for item in recipe.items:
        items.append(item)
        if item.type == recipe_item_type.SEMI_FINISHED:
            items.extend(get_all_items_from_item(item))
    return items


def get_all_items_from_item(item):
    """Рекурсивно получить вложенные позиции полуфабриката"""
    items = []
    for sub_item in item.items:
        items.append(sub_item)
        if sub_item.type == recipe_item_type.SEMI_FINISHED:
            items.extend(get_all_items_from_item(sub_item))
    return items


# ============================================================
# Тесты для TXT формата
# ============================================================

class TestTxtReport:
    """Тесты корректности данных в TXT формате"""

    def test_txt_contains_all_top_level_items(self, factory, complex_recipe):
        """Все позиции верхнего уровня присутствуют в отчете"""
        report = factory.create(report_type_dto.TXT)
        result = report.build(complex_recipe)

        for item in complex_recipe.items:
            assert item.name in result.text, f"Позиция '{item.name}' не найдена в TXT отчете"

    def test_txt_contains_header(self, factory, complex_recipe):
        """Заголовок отчета присутствует"""
        report = factory.create(report_type_dto.TXT)
        result = report.build(complex_recipe)

        assert "Код" in result.text
        assert "Наименование" in result.text
        assert "Брутто" in result.text
        assert "Нетто" in result.text

    def test_txt_contains_separator(self, factory, complex_recipe):
        """Разделитель '|' присутствует в отчете"""
        report = factory.create(report_type_dto.TXT)
        result = report.build(complex_recipe)

        assert "|" in result.text

    def test_txt_line_count_matches_items(self, factory, complex_recipe):
        """Количество строк данных соответствует количеству позиций"""
        report = factory.create(report_type_dto.TXT)
        result = report.build(complex_recipe)

        lines = [l for l in result.text.split("\n") if l.strip()]
        # Первая строка - заголовок, остальные - данные
        data_lines = lines[1:]
        assert len(data_lines) == len(complex_recipe.items)

    def test_txt_contains_weight_values(self, factory, complex_recipe):
        """Значения веса присутствуют в отчете"""
        report = factory.create(report_type_dto.TXT)
        result = report.build(complex_recipe)

        # Проверяем вес курицы (900)
        assert "900" in result.text
        # Проверяем вес моркови (150)
        assert "150" in result.text


# ============================================================
# Тесты для CSV формата
# ============================================================

class TestCsvReport:
    """Тесты корректности данных в CSV формате (бинарные данные)"""

    def test_csv_returns_binary_data(self, factory, complex_recipe):
        """CSV отчет формируется в виде бинарных данных"""
        report = factory.create(report_type_dto.CSV)
        result = report.build(complex_recipe)

        assert len(result.binary) > 0
        assert result.text == ""
        # Бинарные данные корректно декодируются из UTF-8
        assert isinstance(bytes(result.binary).decode("utf-8"), str)

    def test_csv_contains_all_top_level_items(self, factory, complex_recipe):
        """Все позиции верхнего уровня присутствуют в отчете"""
        report = factory.create(report_type_dto.CSV)
        content = report_content(report.build(complex_recipe))

        for item in complex_recipe.items:
            assert item.name in content, f"Позиция '{item.name}' не найдена в CSV отчете"

    def test_csv_contains_header(self, factory, complex_recipe):
        """Заголовок отчета присутствует"""
        report = factory.create(report_type_dto.CSV)
        content = report_content(report.build(complex_recipe))

        assert "Код" in content
        assert "Наименование" in content
        assert "Брутто" in content
        assert "Нетто" in content

    def test_csv_uses_semicolon_separator(self, factory, complex_recipe):
        """Используется разделитель ';'"""
        report = factory.create(report_type_dto.CSV)
        content = report_content(report.build(complex_recipe))

        lines = [l for l in content.split("\n") if l.strip()]
        # Проверяем, что заголовок содержит разделитель
        assert ";" in lines[0]

    def test_csv_line_count_matches_items(self, factory, complex_recipe):
        """Количество строк данных соответствует количеству позиций"""
        report = factory.create(report_type_dto.CSV)
        content = report_content(report.build(complex_recipe))

        lines = [l for l in content.split("\n") if l.strip()]
        data_lines = lines[1:]
        assert len(data_lines) == len(complex_recipe.items)

    def test_csv_contains_weight_values(self, factory, complex_recipe):
        """Значения веса присутствуют в отчете"""
        report = factory.create(report_type_dto.CSV)
        content = report_content(report.build(complex_recipe))

        assert "900" in content
        assert "150" in content

    def test_csv_escapes_semicolons_in_names(self, factory):
        """Проверка экранирования разделителя в названиях"""
        gram = range_model("грамм", 1)
        item = recipe_item_model.create_ingredient("Продукт; особый", 100, gram)
        recipe = recipe_model.create("Тест", "Описание")
        recipe.add_item(item)

        report = factory.create(report_type_dto.CSV)
        content = report_content(report.build(recipe))

        # Название с ';' должно быть заменено на ','
        assert "Продукт, особый" in content


# ============================================================
# Тесты для Markdown формата
# ============================================================

class TestMarkdownReport:
    """Тесты корректности данных в Markdown формате (бинарные данные)"""

    def test_markdown_returns_binary_data(self, factory, complex_recipe):
        """Markdown отчет формируется в виде бинарных данных"""
        report = factory.create(report_type_dto.MARKDOWN)
        result = report.build(complex_recipe)

        assert len(result.binary) > 0
        assert result.text == ""
        # Бинарные данные корректно декодируются из UTF-8
        assert isinstance(bytes(result.binary).decode("utf-8"), str)

    def test_markdown_contains_all_top_level_items(self, factory, complex_recipe):
        """Все позиции верхнего уровня присутствуют в отчете"""
        report = factory.create(report_type_dto.MARKDOWN)
        content = report_content(report.build(complex_recipe))

        for item in complex_recipe.items:
            assert item.name in content, f"Позиция '{item.name}' не найдена в Markdown отчете"

    def test_markdown_contains_table_header(self, factory, complex_recipe):
        """Заголовок таблицы присутствует"""
        report = factory.create(report_type_dto.MARKDOWN)
        content = report_content(report.build(complex_recipe))

        assert "| Код |" in content
        assert "| Наименование |" in content
        assert "| Брутто |" in content
        assert "| Нетто |" in content

    def test_markdown_contains_table_separator(self, factory, complex_recipe):
        """Разделитель таблицы присутствует"""
        report = factory.create(report_type_dto.MARKDOWN)
        content = report_content(report.build(complex_recipe))

        assert "|-----|" in content

    def test_markdown_line_count_matches_items(self, factory, complex_recipe):
        """Количество строк данных соответствует количеству позиций"""
        report = factory.create(report_type_dto.MARKDOWN)
        content = report_content(report.build(complex_recipe))

        lines = [l for l in content.split("\n") if l.strip()]
        # Первая строка - заголовок, вторая - разделитель, остальные - данные
        data_lines = lines[2:]
        assert len(data_lines) == len(complex_recipe.items)

    def test_markdown_contains_weight_values(self, factory, complex_recipe):
        """Значения веса присутствуют в отчете"""
        report = factory.create(report_type_dto.MARKDOWN)
        content = report_content(report.build(complex_recipe))

        assert "900" in content
        assert "150" in content

    def test_markdown_escapes_pipes_in_names(self, factory):
        """Проверка экранирования '|' в названиях"""
        gram = range_model("грамм", 1)
        item = recipe_item_model.create_ingredient("Продукт | особый", 100, gram)
        recipe = recipe_model.create("Тест", "Описание")
        recipe.add_item(item)

        report = factory.create(report_type_dto.MARKDOWN)
        content = report_content(report.build(recipe))

        # Название с '|' должно быть экранировано
        assert "Продукт \\| особый" in content


# ============================================================
# Тесты для XML формата
# ============================================================

class TestXmlReport:
    """Тесты корректности данных в XML формате"""

    def test_xml_contains_all_top_level_items(self, factory, complex_recipe):
        """Все позиции верхнего уровня присутствуют в отчете"""
        report = factory.create(report_type_dto.XML)
        result = report.build(complex_recipe)

        for item in complex_recipe.items:
            assert item.name in result.text, f"Позиция '{item.name}' не найдена в XML отчете"

    def test_xml_contains_valid_xml_declaration(self, factory, complex_recipe):
        """XML декларация присутствует"""
        report = factory.create(report_type_dto.XML)
        result = report.build(complex_recipe)

        assert '<?xml version="1.0" encoding="UTF-8"?>' in result.text

    def test_xml_contains_report_root_element(self, factory, complex_recipe):
        """Корневой элемент <report> присутствует"""
        report = factory.create(report_type_dto.XML)
        result = report.build(complex_recipe)

        assert "<report>" in result.text
        assert "</report>" in result.text

    def test_xml_contains_items_container(self, factory, complex_recipe):
        """Контейнер <items> присутствует"""
        report = factory.create(report_type_dto.XML)
        result = report.build(complex_recipe)

        assert "<items>" in result.text
        assert "</items>" in result.text

    def test_xml_contains_item_elements(self, factory, complex_recipe):
        """Элементы <item> присутствуют для каждой позиции"""
        report = factory.create(report_type_dto.XML)
        result = report.build(complex_recipe)

        item_count = result.text.count("<item>")
        assert item_count == len(complex_recipe.items)

    def test_xml_contains_code_name_brutto_netto_tags(self, factory, complex_recipe):
        """Теги <code>, <name>, <brutto>, <netto> присутствуют"""
        report = factory.create(report_type_dto.XML)
        result = report.build(complex_recipe)

        assert "<code>" in result.text
        assert "<name>" in result.text
        assert "<brutto>" in result.text
        assert "<netto>" in result.text

    def test_xml_contains_weight_values(self, factory, complex_recipe):
        """Значения веса присутствуют в отчете"""
        report = factory.create(report_type_dto.XML)
        result = report.build(complex_recipe)

        assert "900" in result.text
        assert "150" in result.text

    def test_xml_escapes_special_characters(self, factory):
        """Проверка экранирования специальных XML символов"""
        gram = range_model("грамм", 1)
        item = recipe_item_model.create_ingredient("Продукт <особый> & \"важный\"", 100, gram)
        recipe = recipe_model.create("Тест", "Описание")
        recipe.add_item(item)

        report = factory.create(report_type_dto.XML)
        result = report.build(recipe)

        # Специальные символы должны быть экранированы
        assert "&lt;" in result.text or "<особый>" not in result.text


# ============================================================
# Тесты для HTML формата
# ============================================================

class TestHtmlReport:
    """Тесты корректности данных в HTML формате"""

    def test_html_contains_all_top_level_items(self, factory, complex_recipe):
        """Все позиции верхнего уровня присутствуют в отчете"""
        report = factory.create(report_type_dto.HTML)
        result = report.build(complex_recipe)

        for item in complex_recipe.items:
            assert item.name in result.text, f"Позиция '{item.name}' не найдена в HTML отчете"

    def test_html_contains_doctype(self, factory, complex_recipe):
        """DOCTYPE присутствует"""
        report = factory.create(report_type_dto.HTML)
        result = report.build(complex_recipe)

        assert "<!DOCTYPE html>" in result.text

    def test_html_contains_html_structure(self, factory, complex_recipe):
        """HTML структура присутствует"""
        report = factory.create(report_type_dto.HTML)
        result = report.build(complex_recipe)

        assert "<html>" in result.text
        assert "</html>" in result.text
        assert "<head>" in result.text
        assert "</head>" in result.text
        assert "<body>" in result.text
        assert "</body>" in result.text

    def test_html_contains_table(self, factory, complex_recipe):
        """Таблица присутствует"""
        report = factory.create(report_type_dto.HTML)
        result = report.build(complex_recipe)

        assert "<table>" in result.text
        assert "</table>" in result.text

    def test_html_contains_table_headers(self, factory, complex_recipe):
        """Заголовки таблицы присутствуют"""
        report = factory.create(report_type_dto.HTML)
        result = report.build(complex_recipe)

        assert "<th>Код</th>" in result.text
        assert "<th>Наименование</th>" in result.text
        assert "<th>Брутто</th>" in result.text
        assert "<th>Нетто</th>" in result.text

    def test_html_contains_table_rows(self, factory, complex_recipe):
        """Строки таблицы присутствуют для каждой позиции"""
        report = factory.create(report_type_dto.HTML)
        result = report.build(complex_recipe)

        row_count = result.text.count("<tr>")
        # Первая строка - заголовок, остальные - данные
        assert row_count == len(complex_recipe.items) + 1

    def test_html_contains_weight_values(self, factory, complex_recipe):
        """Значения веса присутствуют в отчете"""
        report = factory.create(report_type_dto.HTML)
        result = report.build(complex_recipe)

        assert "900" in result.text
        assert "150" in result.text

    def test_html_escapes_special_characters(self, factory):
        """Проверка экранирования специальных HTML символов"""
        gram = range_model("грамм", 1)
        item = recipe_item_model.create_ingredient("Продукт <особый> & \"важный\"", 100, gram)
        recipe = recipe_model.create("Тест", "Описание")
        recipe.add_item(item)

        report = factory.create(report_type_dto.HTML)
        result = report.build(recipe)

        # Специальные символы должны быть экранированы
        assert "&lt;" in result.text or "<особый>" not in result.text



