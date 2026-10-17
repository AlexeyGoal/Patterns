from flask import Flask, Response, request
from Src.Logics.settings_manager import settings_manager
from Src.Logics.storage_manager import storage_manager
from Src.Logics.report_factory import report_factory
from Src.Dtos.report_type_dto import report_type_dto
from Src.Models.recipe_model import recipe_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.storage_model import storage_model


"""
Точка входа веб-приложения API формирования отчетов.
"""
app = Flask(__name__)

# Инициализация менеджеров настроек и хранилища данных (первый старт)
settings = settings_manager()
settings.load()

storage = storage_manager()
storage.convert()

factory = report_factory()


# Вывод доступных сущностей и ссылок на их отчеты (id генерируется при каждом старте)
_STARTUP_ENTITIES = (
    ("recipe", "Рецепт", storage.recipes),
    ("nomenclature", "Номенклатура", storage.nomenclatures),
    ("range", "Единица измерения", storage.ranges),
    ("storage", "Склад", storage.storages),
)

for _entity_type, _title, _items in _STARTUP_ENTITIES:
    for _item in _items.values():
        print(f"{_title}: {_item.name} (id: {_item.id})")
        print(f"  HTML отчет:  http://localhost:8080/api/report/{_entity_type}/{_item.id}/html")
        print(f"  Формат из настроек: http://localhost:8080/api/report_default/{_entity_type}/{_item.id}")


# Маппинг: строковый тип сущности -> класс модели
ENTITY_TYPE_MAPPING = {
    "recipe": recipe_model,
    "nomenclature": nomenclature_model,
    "range": range_model,
    "storage": storage_model,
}

# Маппинг: формат ответа -> тип отчета
FORMAT_MAPPING = {
    "txt": report_type_dto.TXT,
    "text": report_type_dto.TXT,
    "csv": report_type_dto.CSV,
    "markdown": report_type_dto.MARKDOWN,
    "xml": report_type_dto.XML,
    "html": report_type_dto.HTML,
}

# Форматы, для которых отчет формируется в виде бинарных данных и отдается скачиванием файла
BINARY_DOWNLOAD_FORMATS = {
    "csv": "csv",
    "markdown": "md",
}


@app.route("/")
@app.route("/api/get_report", methods=["GET"])
def get_report():
    """
    HTTP GET endpoint формирования отчета по рецепту.
    :return: Текстовый результат формирования отчета или сообщение об ошибке
    """
    if not storage.recipes:
        return Response("Рецепты в хранилище не найдены", status=404, mimetype="text/plain; charset=utf-8")

    # Берем первый доступный рецепт из первого старта
    recipe = next(iter(storage.recipes.values()))

    report = factory.create(report_type_dto.TXT)
    result = report.build(recipe)

    return Response(result.text, status=200, mimetype="text/plain; charset=utf-8")


@app.route("/api/report/<entity_type>/<entity_code>", methods=["GET"])
@app.route("/api/report/<entity_type>/<entity_code>/<report_format>", methods=["GET"])
def get_entity_report(entity_type: str, entity_code: str, report_format: str = "txt"):
    """
    HTTP GET endpoint формирования отчета для указанного типа сущности и кода.

    Параметры URL:
        entity_type: Тип сущности (recipe, nomenclature, range, storage)
        entity_code: Код (UUID) сущности
        report_format: Формат отчета (txt, csv, markdown, xml, html)

    Примеры:
        /api/report/recipe/<uuid>
        /api/report/recipe/<uuid>/csv
        /api/report/nomenclature/<uuid>/markdown
        /api/report/range/<uuid>/xml
        /api/report/storage/<uuid>/html

    Форматы csv и markdown формируются в виде бинарных данных
    и отдаются скачиванием файла (Content-Disposition: attachment).
    Остальные форматы возвращаются в виде структурированного текста.

    :return: Результат формирования отчета или сообщение об ошибке
    """
    # Валидация типа сущности
    entity_type_lower = entity_type.lower()
    if entity_type_lower not in ENTITY_TYPE_MAPPING:
        return _make_error_response(
            f"Неподдерживаемый тип сущности: '{entity_type}'. "
            f"Допустимые значения: {', '.join(ENTITY_TYPE_MAPPING.keys())}",
            status=400
        )

    # Валидация формата отчета
    format_lower = report_format.lower()
    if format_lower not in FORMAT_MAPPING:
        return _make_error_response(
            f"Неподдерживаемый формат отчета: '{report_format}'. "
            f"Допустимые значения: {', '.join(FORMAT_MAPPING.keys())}",
            status=400
        )

    # Поиск сущности по коду
    entity = _find_entity_by_code(entity_type_lower, entity_code)
    if entity is None:
        return _make_error_response(
            f"Сущность типа '{entity_type}' с кодом '{entity_code}' не найдена",
            status=404
        )

    # Формирование отчета
    report_type = FORMAT_MAPPING[format_lower]
    report = factory.create(report_type)
    result = report.build(entity)

    return _build_report_response(result, format_lower, entity_type_lower, entity_code)


@app.route("/api/report_default/<entity_type>/<entity_code>", methods=["GET"])
def get_entity_report_by_settings(entity_type: str, entity_code: str):
    """
    HTTP GET endpoint формирования отчета в формате из настроек приложения (response_format).

    Использует метод create_default() фабрики: формат отчета (CSV, Markdown, XML, TXT, HTML)
    определяется полем response_format из settings.json.

    Параметры URL:
        entity_type: Тип сущности (recipe, nomenclature, range, storage)
        entity_code: Код (UUID) сущности

    Примеры:
        /api/report_default/recipe/<uuid>
        /api/report_default/nomenclature/<uuid>
        /api/report_default/range/<uuid>

    Форматы csv и markdown (если указаны в настройках) формируются в виде бинарных данных
    и отдаются скачиванием файла (Content-Disposition: attachment).
    Остальные форматы возвращаются в виде структурированного текста.

    :return: Результат формирования отчета или сообщение об ошибке
    """
    # Валидация типа сущности
    entity_type_lower = entity_type.lower()
    if entity_type_lower not in ENTITY_TYPE_MAPPING:
        return _make_error_response(
            f"Неподдерживаемый тип сущности: '{entity_type}'. "
            f"Допустимые значения: {', '.join(ENTITY_TYPE_MAPPING.keys())}",
            status=400
        )

    # Поиск сущности по коду
    entity = _find_entity_by_code(entity_type_lower, entity_code)
    if entity is None:
        return _make_error_response(
            f"Сущность типа '{entity_type}' с кодом '{entity_code}' не найдена",
            status=404
        )

    # Формирование отчета в формате из настроек приложения
    report = factory.create_default()
    result = report.build(entity)

    report_format = settings.settings.response_format.lower()

    return _build_report_response(result, report_format, entity_type_lower, entity_code)


def _make_error_response(message: str, status: int) -> Response:
    """
    Формирует текстовый HTTP-ответ с ошибкой.
    :param message: Текст сообщения об ошибке
    :param status: HTTP статус код
    :return: HTTP-ответ с ошибкой
    """
    return Response(message, status=status, mimetype="text/plain; charset=utf-8")


def _build_report_response(result, report_format: str, entity_type: str, entity_code: str) -> Response:
    """
    Формирует HTTP-ответ отчета в зависимости от формата:
    для бинарных форматов (csv, markdown) - скачивание файла,
    для остальных - структурированный текст.
    :param result: report_result_dto с результатом формирования отчета
    :param report_format: Формат отчета (txt, csv, markdown, xml, html)
    :param entity_type: Тип сущности (recipe, nomenclature, range, storage)
    :param entity_code: Код (UUID) сущности
    :return: HTTP-ответ с отчетом
    """
    if report_format in BINARY_DOWNLOAD_FORMATS:
        return _build_download_response(result, report_format, entity_type, entity_code)

    return Response(result.text, status=200, mimetype=_get_mimetype(report_format))


def _find_entity_by_code(entity_type: str, entity_code: str):
    """
    Поиск сущности по коду в хранилище.
    :param entity_type: Тип сущности (recipe, nomenclature, range, storage)
    :param entity_code: Код (UUID) сущности
    :return: Найденная сущность или None
    """
    if entity_type == "recipe":
        for recipe in storage.recipes.values():
            if str(recipe.id) == entity_code:
                return recipe
    elif entity_type == "nomenclature":
        for nomenclature in storage.nomenclatures.values():
            if str(nomenclature.id) == entity_code:
                return nomenclature
    elif entity_type == "range":
        for range_item in storage.ranges.values():
            if str(range_item.id) == entity_code:
                return range_item
    elif entity_type == "storage":
        for storage_item in storage.storages.values():
            if str(storage_item.id) == entity_code:
                return storage_item
    return None


def _get_mimetype(report_format: str) -> str:
    """
    Определение MIME-типа по формату отчета.
    :param report_format: Формат отчета
    :return: MIME-тип
    """
    mime_types = {
        "txt": "text/plain; charset=utf-8",
        "text": "text/plain; charset=utf-8",
        "csv": "text/csv; charset=utf-8",
        "markdown": "text/markdown; charset=utf-8",
        "xml": "application/xml; charset=utf-8",
        "html": "text/html; charset=utf-8",
    }
    return mime_types.get(report_format, "text/plain; charset=utf-8")


def _build_download_response(result, report_format: str, entity_type: str, entity_code: str) -> Response:
    """
    Формирует HTTP-ответ со скачиванием файла из бинарных данных отчета.
    :param result: report_result_dto с бинарным содержимым отчета
    :param report_format: Формат отчета (csv, markdown)
    :param entity_type: Тип сущности (recipe, nomenclature, range, storage)
    :param entity_code: Код (UUID) сущности
    :return: HTTP-ответ с заголовком Content-Disposition: attachment
    """
    extension = BINARY_DOWNLOAD_FORMATS.get(report_format, report_format)
    filename = f"{entity_type}_{entity_code}.{extension}"

    data = bytes(result.binary) if result.binary else b""

    return Response(
        data,
        status=200,
        mimetype=_get_mimetype(report_format),
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)