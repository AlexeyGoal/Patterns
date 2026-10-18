from flask import Flask, Response
from Src.Logics.settings_manager import settings_manager
from Src.Logics.storage_manager import storage_manager
from Src.Logics.report_factory import report_factory
from Src.Dtos.report_type_dto import report_type_dto


"""
Точка входа веб-приложения API формирования отчетов.

HTTP-слой: маршрутизация и формирование HTTP-ответов.
Поиск сущностей делегирован storage_manager, подбор и создание отчета - report_factory,
способ доставки результата (MIME-тип, скачивание) знает сам отчет.
"""
app = Flask(__name__)

# Инициализация сервисов приложения (первый старт)
settings = settings_manager()
settings.load()

storage = storage_manager()
storage.convert()

factory = report_factory()


# Вывод доступных сущностей и ссылок на их отчеты (id генерируется при каждом старте)
_STARTUP_TITLES = {
    "recipe": "Рецепт",
    "nomenclature": "Номенклатура",
    "range": "Единица измерения",
}

for _entity_type, _title in _STARTUP_TITLES.items():
    for _item in storage.all(_entity_type):
        print(f"{_title}: {_item.name} (id: {_item.id})")
        print(f"  HTML отчет:  http://localhost:8080/api/report/{_entity_type}/{_item.id}/html")
        print(f"  Формат из настроек: http://localhost:8080/api/report_default/{_entity_type}/{_item.id}")


@app.route("/")
@app.route("/api/get_report", methods=["GET"])
def get_report():
    """
    HTTP GET endpoint формирования отчета по первому рецепту.
    :return: Текстовый результат формирования отчета или сообщение об ошибке
    """
    recipes = storage.all("recipe")
    if not recipes:
        return _make_error_response("Рецепты в хранилище не найдены", status=404)

    report = factory.create(report_type_dto.TXT)
    result = report.build(recipes[0])

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
    entity, error = _find_entity(entity_type, entity_code)
    if error is not None:
        return error

    report = factory.create_by_name(report_format)
    if report is None:
        return _make_error_response(
            f"Неподдерживаемый формат отчета: '{report_format}'. "
            f"Допустимые значения: {', '.join(factory.supported_formats)}",
            status=400
        )

    result = report.build(entity)

    return _build_report_response(result, report, entity_type, entity_code)


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

    :return: Результат формирования отчета или сообщение об ошибке
    """
    entity, error = _find_entity(entity_type, entity_code)
    if error is not None:
        return error

    # Формирование отчета в формате из настроек приложения
    report = factory.create_default()
    result = report.build(entity)

    return _build_report_response(result, report, entity_type, entity_code)


def _find_entity(entity_type: str, entity_code: str):
    """
    Поиск сущности в хранилище.
    :param entity_type: Тип сущности (recipe, nomenclature, range, storage)
    :param entity_code: Код (UUID) сущности
    :return: Кортеж (сущность, ответ об ошибке) - ровно одно из значений не None
    """
    if not storage.supports(entity_type):
        return None, _make_error_response(
            f"Неподдерживаемый тип сущности: '{entity_type}'. "
            f"Допустимые значения: {', '.join(storage.supported_types)}",
            status=400
        )

    entity = storage.find(entity_type, entity_code)
    if entity is None:
        return None, _make_error_response(
            f"Сущность типа '{entity_type}' с кодом '{entity_code}' не найдена",
            status=404
        )

    return entity, None


def _build_report_response(result, report, entity_type: str, entity_code: str) -> Response:
    """
    HTTP-ответ отчета: способ доставки (MIME-тип, скачивание) определяет сам отчет.
    :param result: report_result_dto с результатом формирования отчета
    :param report: Экземпляр отчета (наследник abstract_report)
    :param entity_type: Тип сущности (recipe, nomenclature, range, storage)
    :param entity_code: Код (UUID) сущности
    :return: HTTP-ответ с отчетом
    """
    if report.is_download:
        data = bytes(result.binary) if result.binary else b""
        filename = f"{entity_type.strip().lower()}_{entity_code}.{report.extension}"

        return Response(
            data,
            status=200,
            mimetype=report.mimetype,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    return Response(result.text, status=200, mimetype=report.mimetype)


def _make_error_response(message: str, status: int) -> Response:
    """
    Формирует текстовый HTTP-ответ с ошибкой.
    :param message: Текст сообщения об ошибке
    :param status: HTTP статус код
    :return: HTTP-ответ с ошибкой
    """
    return Response(message, status=status, mimetype="text/plain; charset=utf-8")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
