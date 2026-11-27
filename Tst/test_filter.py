import pytest

import main
from Src.Core.exception import arguments_exception
from Src.Core.filter_type import filter_type
from Src.Dtos.filter_dto import filter_dto
from Src.Logics.entity_filter import entity_filter
from Src.Logics.filter_dto_deserializer import filter_dto_deserializer
from Src.Logics.filter_prototype import filter_prototype
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.recipe_model import recipe_model


class TestFilterType:
    """Юнит-тесты перечисления вариантов фильтрации."""

    def test_filter_type_contains_only_required_variants(self):
        """Перечисление содержит только полное совпадение и вхождение строки."""
        assert list(filter_type) == [filter_type.EQUALS, filter_type.LIKE]
        assert filter_type.EQUALS.value == "equals"
        assert filter_type.LIKE.value == "like"


class TestFilterDto:
    """Юнит-тесты DTO фильтрации."""

    def test_dto_stores_entity_field_value_and_mode(self):
        """DTO сохраняет тип модели, поле, значение и вариант сравнения."""
        query = filter_dto("nomenclature", "name", "Мука", filter_type.LIKE)

        assert query.entity_type == "nomenclature"
        assert query.field_name == "name"
        assert query.value == "Мука"
        assert query.filter_type is filter_type.LIKE

    def test_dto_uses_equals_by_default(self):
        """Если вариант не указан, используется полное совпадение."""
        query = filter_dto("nomenclature", "name", "Мука")

        assert query.filter_type is filter_type.EQUALS

    def test_dto_rejects_non_enum_filter_type(self):
        """DTO принимает только значения перечисления filter_type."""
        with pytest.raises(arguments_exception):
            filter_dto("nomenclature", "name", "Мука", "LIKE")

    def test_dto_does_not_hardcode_domain_models_and_fields(self):
        """DTO принимает любую модель и поле: их проверяет сервис по модели."""
        query = filter_dto("custom_model", "custom_field", "value")

        assert query.entity_type == "custom_model"
        assert query.field_name == "custom_field"

    def test_dto_rejects_empty_parameters(self):
        """DTO отвергает пустой тип модели, поле и значение."""
        with pytest.raises(arguments_exception):
            filter_dto("", "name", "Мука")

        with pytest.raises(arguments_exception):
            filter_dto("group", "", "Мука")

        with pytest.raises(arguments_exception):
            filter_dto("group", "name", "")


class TestEntityFilter:
    """Юнит-тесты применения DTO к доменным моделям."""

    def test_equals_and_like_by_name(self):
        """EQUALS ищет полное совпадение, LIKE — вхождение строки."""
        items = [
            nomenclature_model.create_flour(),
            nomenclature_model.create_milk(),
        ]
        filter_logic = entity_filter()

        equals = filter_dto("nomenclature", "name", "Мука пшеничная", filter_type.EQUALS)
        like = filter_dto("nomenclature", "name", "молоко", filter_type.LIKE)

        assert [item.name for item in filter_logic.apply(items, equals)] == ["Мука пшеничная"]
        assert [item.name for item in filter_logic.apply(items, like)] == ["Молоко 3.2%"]

    def test_filter_by_unique_code(self):
        """Фильтрация по коду сравнивает UUID сущности."""
        recipe = recipe_model.create("Тестовый рецепт", "Описание")
        query = filter_dto("recipe", "code", str(recipe.id), filter_type.EQUALS)

        assert entity_filter().apply([recipe], query) == [recipe]

    def test_filter_by_unique_code_alias(self):
        """Псевдоним unique_code разрешается по FIELD_ALIASES модели."""
        recipe = recipe_model.create("Тестовый рецепт", "Описание")
        query = filter_dto("recipe", "unique_code", str(recipe.id), filter_type.EQUALS)

        assert entity_filter().apply([recipe], query) == [recipe]

    def test_filters_by_any_field_declared_in_model(self):
        """Любое поле модели доступно без изменения DTO и фильтра."""
        items = [
            nomenclature_model.create_flour(),
            nomenclature_model.create_milk(),
        ]
        query = filter_dto("nomenclature", "full_name", "высший", filter_type.LIKE)

        assert [
            item.name for item in entity_filter().apply(items, query)
        ] == ["Мука пшеничная"]

    def test_searches_nested_base_range_by_name(self):
        """Поиск по наименованию находит совпадение в базовой единице измерения."""
        gram = range_model.create_gram()
        kilogram = range_model("килограмм", 1000, gram)
        liter = range_model.create_liter()

        query = filter_dto("range", "name", "грамм", filter_type.EQUALS)

        assert entity_filter().apply([kilogram, liter], query) == [kilogram]

    def test_searches_nested_base_range_by_code(self):
        """Поиск по коду находит базовую единицу измерения по её UUID."""
        gram = range_model.create_gram()
        kilogram = range_model("килограмм", 1000, gram)

        query = filter_dto("range", "code", str(gram.id), filter_type.EQUALS)

        assert entity_filter().apply([kilogram], query) == [kilogram]

    def test_searches_nested_parent_group(self):
        """Поиск по наименованию находит родительскую группу."""
        parent = nomenclature_group_model.create_grocery()
        child = nomenclature_group_model("Крупы", parent=parent)

        query = filter_dto("group", "name", "Бакалея", filter_type.EQUALS)

        assert entity_filter().apply([child], query) == [child]

    def test_searches_nested_parent_group_by_owner_alias(self):
        """Связь группы-владельца доступна через псевдоним owner."""
        parent = nomenclature_group_model.create_grocery()
        child = nomenclature_group_model("Крупы", owner=parent)

        assert child.owner is parent
        assert child.parent is parent

    def test_unknown_field_raises_error(self):
        """Несуществующее поле модели приводит к ошибке."""
        with pytest.raises(arguments_exception):
            entity_filter().apply(
                [nomenclature_model.create_flour()],
                filter_dto("nomenclature", "unknown_field", "value"),
            )


class TestFilterDtoDeserializer:
    """Тесты восстановления DTO фильтрации механизмом десериализации."""

    def test_deserializes_dict_to_filter_dto(self):
        """Словарь восстанавливается в готовый объект filter_dto."""
        query = filter_dto_deserializer().deserialize({
            "entity_type": "nomenclature",
            "field_name": "name",
            "value": "Мука",
            "filter_type": "LIKE",
        })

        assert isinstance(query, filter_dto)
        assert query.entity_type == "nomenclature"
        assert query.field_name == "name"
        assert query.value == "Мука"
        assert query.filter_type is filter_type.LIKE

    def test_deserializes_field_aliases(self):
        """Псевдонимы field и entity приводятся к каноническим именам."""
        query = filter_dto_deserializer().deserialize({
            "entity": "nomenclature",
            "field": "name",
            "value": "Мука",
        })

        assert query.entity_type == "nomenclature"
        assert query.field_name == "name"
        assert query.filter_type is filter_type.EQUALS

    def test_entity_type_from_route_overrides_body(self):
        """Тип модели из route имеет приоритет над телом запроса."""
        query = filter_dto_deserializer().deserialize(
            {
                "entity_type": "range",
                "field_name": "name",
                "value": "грамм",
            },
            entity_type="nomenclature",
        )

        assert query.entity_type == "nomenclature"

    def test_invalid_filter_type_raises_error(self):
        """Неизвестный вариант фильтрации приводит к ошибке."""
        with pytest.raises(arguments_exception):
            filter_dto_deserializer().deserialize({
                "entity_type": "nomenclature",
                "field_name": "name",
                "value": "Мука",
                "filter_type": "UNKNOWN",
            })


class TestFilterPrototype:
    """Тесты шаблона «Прототип»."""

    def test_clone_contains_filtered_items(self):
        """Клон прототипа сразу содержит отфильтрованный список."""
        prototype = filter_prototype(items=[
            nomenclature_model.create_flour(),
            nomenclature_model.create_milk(),
        ])
        query = filter_dto("nomenclature", "name", "Мука", filter_type.LIKE)

        clone = prototype.clone(query)

        assert clone is not prototype
        assert prototype.query is None
        assert clone.query is query
        assert [item.name for item in clone.items] == ["Мука пшеничная"]
        assert len(prototype.items) == 2

    def test_one_prototype_filters_different_domain_models(self):
        """Один прототип используется для разных доменных моделей."""
        source = {
            "nomenclature": [
                nomenclature_model.create_flour(),
                nomenclature_model.create_milk(),
            ],
            "range": [
                range_model.create_gram(),
                range_model.create_liter(),
            ],
        }
        prototype = filter_prototype(source=lambda entity_type: source[entity_type])

        nomenclature_query = filter_dto("nomenclature", "name", "Мука", filter_type.LIKE)
        range_query = filter_dto("range", "name", "грамм", filter_type.EQUALS)

        nomenclatures = prototype.clone(nomenclature_query).items
        ranges = prototype.clone(range_query).items

        assert [item.name for item in nomenclatures] == ["Мука пшеничная"]
        assert [item.name for item in ranges] == ["грамм"]

    def test_unconfigured_prototype_requires_dto(self):
        """Не настроенный прототип не выполняет фильтрацию."""
        with pytest.raises(arguments_exception):
            filter_prototype(items=[nomenclature_model.create_flour()]).clone()


class TestEntityServiceFilter:
    """Проверка фильтрации через сервис доменных сущностей."""

    def test_service_filters_nomenclature_by_name(self):
        """Сервис возвращает отфильтрованные сущности в JSON-виде."""
        query = filter_dto("nomenclature", "name", "Мука", filter_type.LIKE)

        result = main.entities.filter_entities("nomenclature", query)

        assert [item["name"] for item in result] == ["Мука пшеничная"]

    def test_service_rejects_unknown_entity_type(self):
        """Сервис проверяет тип модели по зарегистрированным сущностям."""
        query = filter_dto("unknown", "name", "value")

        with pytest.raises(arguments_exception):
            main.entities.filter_entities("unknown", query)


@pytest.fixture
def client():
    """Клиент Flask для проверки POST-фильтрации."""
    main.app.config["TESTING"] = True
    with main.app.test_client() as client:
        yield client


class TestFilterApi:
    """Интеграционные тесты POST-фильтрации."""

    def test_post_filter_uses_entity_type_from_route(self, client):
        """Тип доменной модели берётся из route."""
        response = client.post(
            "/api/filter/nomenclature",
            json={
                "field_name": "name",
                "value": "Мука",
                "filter_type": "LIKE",
            },
        )

        assert response.status_code == 200
        assert [item["name"] for item in response.get_json()] == ["Мука пшеничная"]

    def test_post_filter_searches_nested_structures(self, client):
        """POST-фильтрация находит совпадения во вложенных сущностях."""
        response = client.post(
            "/api/filter/range",
            json={
                "field_name": "name",
                "value": "грамм",
                "filter_type": "EQUALS",
            },
        )

        assert response.status_code == 200
        assert {item["name"] for item in response.get_json()} == {
            "грамм",
            "килограмм",
        }

    def test_post_filter_rejects_unknown_entity_type(self, client):
        """Неизвестный тип доменной модели возвращает HTTP 400."""
        response = client.post(
            "/api/filter/unknown",
            json={
                "field_name": "name",
                "value": "x",
                "filter_type": "EQUALS",
            },
        )

        assert response.status_code == 400

    def test_post_filter_rejects_invalid_dto(self, client):
        """Некорректный вариант фильтрации возвращает HTTP 400."""
        response = client.post(
            "/api/filter/nomenclature",
            json={
                "field_name": "name",
                "value": "Мука",
                "filter_type": "UNKNOWN",
            },
        )

        assert response.status_code == 400
