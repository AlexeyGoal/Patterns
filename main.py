import datetime
import os
import time
from flask import Flask, Response, g, jsonify, redirect, request, send_from_directory
from Src.Core.exception import arguments_exception
from Src.Core.log_type import log_category, log_operation, log_status
from Src.Core.validator import argument_exception, operation_exception
from Src.Logics.entity_service import entity_service
from Src.Logics.logging_service import logging_service
from Src.Logics.settings_manager import settings_manager
from Src.Logics.storage_manager import storage_manager
from Src.Logics.report_factory import report_factory
from Src.Logics.filter_dto_deserializer import filter_dto_deserializer
from Src.Dtos.filter_dto import filter_dto
from Src.Dtos.report_type_dto import report_type_dto

try:
    from flask_swagger_ui import get_swaggerui_blueprint
except ImportError:  # pragma: no cover - запасной вариант без установленного пакета
    get_swaggerui_blueprint = None


"""
Точка входа веб-приложения API формирования отчетов.
"""
app = Flask(__name__)
app.url_map.strict_slashes = False

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OPENAPI_FILE = "openapi.yaml"

# Инициализация сервисов приложения (первый старт)
settings = settings_manager()
settings.load()

storage = storage_manager()
storage.convert()

factory = report_factory()
entities = entity_service(storage)
filter_deserializer = filter_dto_deserializer()

# Субъект журналирования: получает события от CRUD, склада, Web и настроек
audit_log = logging_service()


@app.before_request
def _start_request_timer():
    """
    Запоминает начало обработки HTTP-запроса для журнала Web-вызовов.
    """
    g.request_started_at = time.perf_counter()


@app.after_request
def _log_web_request(response):
    """
    Фиксирует вызов Web-метода: маршрут, результат и длительность обработки.
    """
    started_at = getattr(g, "request_started_at", None)
    duration_ms = (
        round((time.perf_counter() - started_at) * 1000, 2)
        if started_at is not None
        else None
    )

    try:
        audit_log.log(
            category=log_category.WEB,
            operation=log_operation.CALL,
            status=(
                log_status.SUCCESS
                if response.status_code < 400
                else log_status.FAILURE
            ),
            message=f"{request.method} {request.path} -> {response.status_code}",
            details={
                "method": request.method,
                "path": request.path,
                "endpoint": request.endpoint or "",
                "status_code": response.status_code,
                "duration_ms": duration_ms,
                "remote_addr": request.remote_addr or "",
                "query": request.query_string.decode("utf-8", errors="ignore"),
            },
            source="web",
        )
    except Exception:
        # Сбой журналирования не должен ломать HTTP-ответ.
        pass

    return response


SWAGGER_URL = "/api/docs"
OPENAPI_URL = "/openapi.yaml"

if get_swaggerui_blueprint is not None:
    app.register_blueprint(
        get_swaggerui_blueprint(
            SWAGGER_URL,
            OPENAPI_URL,
            config={"app_name": "API формирования отчетов"},
        ),
        url_prefix=SWAGGER_URL,
    )
else:  
    @app.route(SWAGGER_URL, methods=["GET"])
    def swagger_ui():
        """Запасная страница Swagger UI (CDN) без пакета flask-swagger-ui."""
        return Response(
            f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Swagger UI</title>
  <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css">
</head>
<body>
  <div id="swagger-ui"></div>
  <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
  <script>
    SwaggerUIBundle({{ url: "{OPENAPI_URL}", dom_id: "#swagger-ui" }});
  </script>
</body>
</html>""",
            status=200,
            mimetype="text/html",
        )


@app.route(OPENAPI_URL, methods=["GET"])
@app.route("/api/openapi.yaml", methods=["GET"])
def openapi_spec():
    """Спецификация OpenAPI в формате YAML."""
    return send_from_directory(BASE_DIR, OPENAPI_FILE, mimetype="application/yaml")


@app.route("/swagger", methods=["GET"])
@app.route("/docs", methods=["GET"])
@app.route("/apidocs", methods=["GET"])
@app.route("/swagger-ui", methods=["GET"])
def swagger_redirect():
    """Короткие адреса для перехода к Swagger UI."""
    return redirect(SWAGGER_URL)


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
   
    """
    recipes = storage.all("recipe")
    if not recipes:
        return _make_error_response("Рецепты в хранилище не найдены", status=404)

    report = factory.create(report_type_dto.TXT)
    result = report.build(recipes[0])

    return Response(result.text, status=200, mimetype="text/plain; charset=utf-8")




@app.route("/api/formats", methods=["GET"])
@app.route("/api/get_formats", methods=["GET"])
def get_report_formats():
    """
    HTTP GET endpoint получения списка всех форматов для построения отчетов.
    """
    return jsonify(factory.formats)


@app.route("/api/formats/details", methods=["GET"])
def get_report_formats_details():
    """
    HTTP GET endpoint получения подробного описания форматов отчетов.
    """
    return jsonify(factory.format_details())


@app.route("/api/logs", methods=["GET"])
def get_audit_logs():
    """
    HTTP GET endpoint получения последних событий журнала аудита.
    """
    raw_limit = request.args.get("limit", "100")

    try:
        limit = int(raw_limit)
    except (TypeError, ValueError):
        return _make_json_error("Параметр limit должен быть целым числом", status=400)

    if limit < 0:
        return _make_json_error("Параметр limit не может быть отрицательным", status=400)

    events = audit_log.events(
        category=request.args.get("category"),
        status=request.args.get("status"),
        limit=limit,
    )

    return jsonify(events), 200


@app.route("/api/settings", methods=["GET"])
def get_settings():
    """
    HTTP GET endpoint получения текущих параметров настроек.
    """
    if not settings.is_loaded:
        settings.load()

    return jsonify(settings.to_dict()), 200


@app.route("/api/settings", methods=["PUT", "PATCH"])
def update_settings():
    """
    HTTP PUT/PATCH endpoint изменения параметров настроек.

    Изменение фиксируется в журнале аудита категорией SETTINGS.
    """
    try:
        settings.update(_request_payload())
    except (
        arguments_exception,
        argument_exception,
        operation_exception,
        ValueError,
    ) as ex:
        return _make_json_error(str(ex), status=400)
    except Exception as ex:
        return _make_json_error(f"Ошибка при изменении настроек: {ex}", status=500)

    return jsonify(settings.to_dict()), 200



def _make_json_error(message: str, status: int):
    """
    Формирует JSON-ответ с ошибкой.
    """
    return jsonify({"error": message, "detail": message}), status


def _request_payload() -> dict:
    """
    Извлекает JSON-тело запроса.
    """
    payload = request.get_json(silent=True)
    if payload is None:
        raise arguments_exception("payload", "Тело запроса должно быть JSON-объектом")

    return payload


def _filter_dto_from_payload(entity_type: str, payload: dict) -> filter_dto:
    """
    Создаёт DTO фильтрации из JSON-тела запроса.
    """

    return filter_deserializer.deserialize(payload, entity_type=entity_type)


def _filter_dto_from_body(payload: dict) -> filter_dto:
    """
    Создаёт DTO фильтрации из тела запроса, включая тип доменной модели.

    Тип модели можно передать в поле entity_type. Для ОСВ по умолчанию
    используется номенклатура.
    """

    if not isinstance(payload, dict):
        raise arguments_exception("payload", "Тело запроса должно быть JSON-объектом")

    entity_type = (
        payload.get("entity_type")
        or payload.get("entity")
        or "nomenclature"
    )

    return _filter_dto_from_payload(entity_type, payload)


def _start_date_from_payload(payload: dict):
    """
    Извлекает дату начала периода ОСВ из тела запроса.
    """

    value = payload.get("start_date")

    if value is None or (isinstance(value, str) and value.strip() == ""):
        return None

    if isinstance(value, datetime.datetime):
        return value.date()

    if isinstance(value, datetime.date):
        return value

    try:
        return datetime.date.fromisoformat(str(value).strip())
    except ValueError as error:
        raise arguments_exception(
            "start_date",
            f"Дата начала периода должна быть в формате YYYY-MM-DD: {error}",
        ) from error


@app.route("/api/entities", methods=["GET"])
def list_all_entities():
    """
    HTTP GET endpoint получения всех доменных сущностей по категориям.
    """
    return jsonify({
        entity_type: entities.list_entities(entity_type)
        for entity_type in entities.supported_types
    })


@app.route("/api/entities/<entity_type>", methods=["GET"])
@app.route("/api/entity/<entity_type>", methods=["GET"])
@app.route("/api/<entity_type>", methods=["GET"])
def list_entities(entity_type: str):
    """
    HTTP GET endpoint получения списка доменных сущностей указанного типа.
    """
    if not entities.supports(entity_type):
        return _make_json_error(
            f"Неподдерживаемый тип сущности: '{entity_type}'. "
            f"Допустимые значения: {', '.join(entities.supported_types)}",
            status=400,
        )

    return jsonify(entities.list_entities(entity_type))


@app.route("/api/filter/<entity_type>", methods=["POST"])
def filter_entities(entity_type: str):
    """
    HTTP POST endpoint фильтрации доменных сущностей.

    Тип доменной модели передаётся в route, а в теле запроса — DTO фильтрации:
    field_name, value и filter_type (EQUALS или LIKE).
    """
    if not entities.supports(entity_type):
        return _make_json_error(
            f"Неподдерживаемый тип сущности: '{entity_type}'. "
            f"Допустимые значения: {', '.join(entities.supported_types)}",
            status=400,
        )

    try:
        query = _filter_dto_from_payload(entity_type, _request_payload())
        result = entities.filter_entities(entity_type, query)
    except (arguments_exception, operation_exception) as ex:
        return _make_json_error(str(ex), status=400)
    except Exception as ex:
        return _make_json_error(f"Ошибка при фильтрации сущностей: {ex}", status=500)

    return jsonify(result), 200


@app.route("/api/osv", methods=["POST"])
@app.route("/api/report/osv", methods=["POST"])
def build_osv():
    """
    HTTP POST endpoint формирования оборотно-сальдовой ведомости (ОСВ).

    В теле запроса передаётся DTO фильтрации. Тип доменной модели по умолчанию
    — nomenclature. Возвращается список строк ОСВ, отобранных по фильтру.
    """
    try:
        payload = _request_payload()
        query = _filter_dto_from_body(payload)
        start_date = _start_date_from_payload(payload)
        result = entities.build_osv(query, start_date)
    except (arguments_exception, operation_exception) as ex:
        return _make_json_error(str(ex), status=400)
    except Exception as ex:
        return _make_json_error(f"Ошибка при формировании ОСВ: {ex}", status=500)

    return jsonify(result), 200


@app.route("/api/entities/<entity_type>", methods=["POST"])
@app.route("/api/entity/<entity_type>", methods=["POST"])
@app.route("/api/<entity_type>", methods=["POST"])
def create_entity(entity_type: str):
    """
    HTTP POST endpoint создания доменной сущности.
    """
    try:
        result = entities.create_entity(entity_type, _request_payload())
    except (arguments_exception, operation_exception) as ex:
        return _make_json_error(str(ex), status=400)
    except Exception as ex:
        return _make_json_error(f"Ошибка при создании сущности: {ex}", status=500)

    return jsonify(result), 200


@app.route("/api/entities/<entity_type>/<entity_code>", methods=["GET"])
@app.route("/api/entity/<entity_type>/<entity_code>", methods=["GET"])
@app.route("/api/<entity_type>/<entity_code>", methods=["GET"])
def get_entity(entity_type: str, entity_code: str):
    """
    HTTP GET endpoint получения доменной сущности по коду.
    """
    if not entities.supports(entity_type):
        return _make_json_error(
            f"Неподдерживаемый тип сущности: '{entity_type}'. "
            f"Допустимые значения: {', '.join(entities.supported_types)}",
            status=400,
        )

    result = entities.get_entity(entity_type, entity_code)
    if result is None:
        return _make_json_error(
            f"Сущность типа '{entity_type}' с кодом '{entity_code}' не найдена",
            status=404,
        )

    return jsonify(result)


@app.route("/api/entities/<entity_type>/<entity_code>", methods=["PUT", "PATCH"])
@app.route("/api/entity/<entity_type>/<entity_code>", methods=["PUT", "PATCH"])
@app.route("/api/<entity_type>/<entity_code>", methods=["PUT", "PATCH"])
def update_entity(entity_type: str, entity_code: str):
    """
    HTTP PUT/PATCH endpoint изменения доменной сущности.
    """
    if not entities.supports(entity_type):
        return _make_json_error(
            f"Неподдерживаемый тип сущности: '{entity_type}'. "
            f"Допустимые значения: {', '.join(entities.supported_types)}",
            status=400,
        )

    if entities.get_entity(entity_type, entity_code) is None:
        return _make_json_error(
            f"Сущность типа '{entity_type}' с кодом '{entity_code}' не найдена",
            status=404,
        )

    try:
        result = entities.update_entity(entity_type, entity_code, _request_payload())
    except (arguments_exception, operation_exception) as ex:
        return _make_json_error(str(ex), status=400)
    except Exception as ex:
        return _make_json_error(f"Ошибка при изменении сущности: {ex}", status=500)

    return jsonify(result)


@app.route("/api/entities/<entity_type>/<entity_code>", methods=["DELETE"])
@app.route("/api/entity/<entity_type>/<entity_code>", methods=["DELETE"])
@app.route("/api/<entity_type>/<entity_code>", methods=["DELETE"])
def delete_entity(entity_type: str, entity_code: str):
    """
    HTTP DELETE endpoint удаления доменной сущности.
    """
    if not entities.supports(entity_type):
        return _make_json_error(
            f"Неподдерживаемый тип сущности: '{entity_type}'. "
            f"Допустимые значения: {', '.join(entities.supported_types)}",
            status=400,
        )

    if entities.get_entity(entity_type, entity_code) is None:
        return _make_json_error(
            f"Сущность типа '{entity_type}' с кодом '{entity_code}' не найдена",
            status=404,
        )

    try:
        result = entities.delete_entity(entity_type, entity_code)
    except operation_exception as ex:
        return _make_json_error(str(ex), status=400)
    except Exception as ex:
        return _make_json_error(f"Ошибка при удалении сущности: {ex}", status=500)

    result["deleted"] = True
    return jsonify(result)



@app.route("/api/report/<entity_type>/<entity_code>", methods=["GET"])
@app.route("/api/report/<entity_type>/<entity_code>/<report_format>", methods=["GET"])
def get_entity_report(entity_type: str, entity_code: str, report_format: str = "txt"):
    """
    HTTP GET endpoint формирования отчета для указанного типа сущности и кода.
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
    """
    return Response(message, status=status, mimetype="text/plain; charset=utf-8")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
