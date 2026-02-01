"""Версионирование и миграция формата экспорта."""

from typing import Dict, Any, Callable, List

# Текущая версия формата экспорта
CURRENT_FORMAT_VERSION = "1.0"

# Минимальная поддерживаемая версия
MIN_SUPPORTED_VERSION = "1.0"


def parse_version(version_str: str) -> tuple:
    """Парсинг версии в кортеж для сравнения."""
    parts = version_str.split(".")
    return tuple(int(p) for p in parts)


def is_version_supported(version_str: str) -> bool:
    """Проверка поддержки версии формата."""
    try:
        version = parse_version(version_str)
        min_version = parse_version(MIN_SUPPORTED_VERSION)
        current = parse_version(CURRENT_FORMAT_VERSION)
        return min_version <= version <= current
    except (ValueError, AttributeError):
        return False


# Реестр миграций: (from_version, to_version) -> migration_func
_migrations: Dict[tuple, Callable[[Dict[str, Any]], Dict[str, Any]]] = {}


def register_migration(
    from_version: str,
    to_version: str
) -> Callable:
    """Декоратор для регистрации функции миграции.

    Пример:
        @register_migration("1.0", "1.1")
        def migrate_1_0_to_1_1(data: Dict) -> Dict:
            # Модификация формата
            return data
    """
    def decorator(func: Callable[[Dict[str, Any]], Dict[str, Any]]) -> Callable:
        _migrations[(from_version, to_version)] = func
        return func
    return decorator


def get_migration_path(from_version: str, to_version: str) -> List[str]:
    """Построить путь миграции между версиями.

    Возвращает список версий для последовательной миграции.
    """
    if from_version == to_version:
        return []

    path = [from_version]
    current = from_version

    while current != to_version:
        next_version = None
        for (fv, tv) in _migrations.keys():
            if fv == current:
                next_version = tv
                break

        if next_version is None:
            raise ValueError(
                f"No migration path from {from_version} to {to_version}"
            )

        path.append(next_version)
        current = next_version

    return path


def migrate_data(data: Dict[str, Any], target_version: str = None) -> Dict[str, Any]:
    """Мигрировать данные до целевой версии.

    По умолчанию мигрирует до текущей версии.
    """
    if target_version is None:
        target_version = CURRENT_FORMAT_VERSION

    current_version = data.get("format_version", "1.0")

    if current_version == target_version:
        return data

    path = get_migration_path(current_version, target_version)

    result = data
    for i in range(len(path) - 1):
        from_v = path[i]
        to_v = path[i + 1]
        migration_func = _migrations.get((from_v, to_v))
        if migration_func:
            result = migration_func(result)
            result["format_version"] = to_v

    return result


# Примеры будущих миграций (пока пустые):
# @register_migration("1.0", "1.1")
# def migrate_1_0_to_1_1(data: Dict[str, Any]) -> Dict[str, Any]:
#     """Пример миграции с 1.0 на 1.1."""
#     # Добавляем новые поля
#     for char in data.get("entities", {}).get("characters", {}).get("data", []):
#         char.setdefault("armor_class", 10)
#     return data
