"""Система сохранения и восстановления сессий."""

from app.services.persistence.session_exporter import export_session
from app.services.persistence.session_importer import (
    import_session,
    validate_import_data,
    ImportResult,
    ValidationResult,
)
from app.services.persistence.registry import registry, SaveableRegistry
from app.services.persistence.types import (
    ExportContext,
    ImportContext,
    IdMapping,
)
from app.services.persistence.migrations import (
    CURRENT_FORMAT_VERSION,
    is_version_supported,
)

__all__ = [
    "export_session",
    "import_session",
    "validate_import_data",
    "ImportResult",
    "ValidationResult",
    "registry",
    "SaveableRegistry",
    "ExportContext",
    "ImportContext",
    "IdMapping",
    "CURRENT_FORMAT_VERSION",
    "is_version_supported",
]
