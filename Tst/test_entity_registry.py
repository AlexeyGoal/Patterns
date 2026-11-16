from Src.Logics.entity_registry import entity_metadata_registry
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.recipe_item_model import recipe_item_model
from Src.Models.recipe_model import recipe_model
from Src.Models.storage_model import storage_model


def test_registry_discovers_api_entities_by_entity_type():
    """Типы API собираются рефлексией по атрибуту ENTITY_TYPE."""

    registry = entity_metadata_registry()

    assert set(registry.types) == {"group", "nomenclature", "range", "recipe", "storage"}
    assert registry.models == {
        "group": nomenclature_group_model,
        "nomenclature": nomenclature_model,
        "range": range_model,
        "recipe": recipe_model,
        "storage": storage_model,
    }


def test_registry_discovers_relations_from_annotations():
    """Связи моделей собираются по аннотациям свойств."""

    registry = entity_metadata_registry()

    relations = registry.get("nomenclature").relations

    assert set(relations) == {"group", "range"}
    assert relations["group"].target is nomenclature_group_model
    assert relations["range"].target is range_model
    assert relations["group"].is_list is False
    assert relations["range"].is_list is False
    assert relations["group"].embedded is False
    assert relations["range"].embedded is False


def test_registry_marks_collections_and_embedded_models():
    """Коллекции и встроенные модели определяются по add_* и составу домена."""

    registry = entity_metadata_registry()

    recipe_relations = registry.get("recipe").relations

    assert set(recipe_relations) == {"items", "packaging", "sub_recipes"}
    assert recipe_relations["items"].target is recipe_item_model
    assert recipe_relations["items"].is_list is True
    assert recipe_relations["items"].embedded is True
    assert recipe_relations["packaging"].is_list is False
    assert recipe_relations["packaging"].embedded is True
    assert recipe_relations["sub_recipes"].is_list is True
    assert recipe_relations["sub_recipes"].embedded is False

    item_metadata = registry.get_by_model(recipe_item_model)

    assert item_metadata is not None
    assert item_metadata.api_type is None
    assert set(item_metadata.relations) == {"items", "range"}
    assert item_metadata.relations["items"].embedded is True
    assert item_metadata.relations["range"].embedded is False


def test_registry_builds_field_aliases_from_relations_and_models():
    """Псевдонимы полей выводятся из связей и объявлений моделей."""

    registry = entity_metadata_registry()

    aliases = registry.aliases_by_model(registry.models["nomenclature"])
    assert aliases["code"] == "id"
    assert aliases["group_id"] == "group"
    assert aliases["range_id"] == "range"
    assert aliases["unit"] == "range"

    recipe_aliases = registry.aliases_by_model(registry.models["recipe"])
    assert recipe_aliases["sub_recipe_ids"] == "sub_recipes"
    assert recipe_aliases["recipe_ids"] == "sub_recipes"

    item_aliases = registry.aliases_by_model(recipe_item_model)
    assert item_aliases["item_type"] == "type"
    assert item_aliases["range_id"] == "range"
