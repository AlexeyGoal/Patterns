from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.storage_model import storage_model


"""
Извлечение полей сущности для формирования отчетов.
Поддерживает типы сущностей, отличные от рецепта: номенклатура, единица измерения, склад.
"""
def extract_entity_fields(source) -> list:
    """
    Извлекает поля сущности в виде списка пар (название поля, значение).
    :param source: Модель сущности (nomenclature_model, range_model, storage_model)
    :return: Список пар (название, значение)
    """
    if isinstance(source, nomenclature_model):
        return [
            ("Наименование", source.name),
            ("Полное наименование", source.full_name),
            ("Группа", source.group.name if source.group else "Не указана"),
            ("Единица измерения", source.range.name if source.range else "Не указана"),
        ]

    if isinstance(source, range_model):
        fields = [
            ("Наименование", source.name),
            ("Коэффициент пересчёта", source.conversion_factor),
        ]
        if source.base_range:
            fields.append(("Базовая единица", source.base_range.name))
        return fields

    if isinstance(source, storage_model):
        return [
            ("Наименование", source.name),
            ("Адрес", source.address),
        ]

    return []
