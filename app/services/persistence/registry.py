"""Registry для сериализаторов сущностей."""

from typing import Type, Dict, List, Any, Optional

from app.services.persistence.serializers.base import Saveable
from app.services.persistence.types import ExportContext, ImportContext


class SaveableRegistry:
    """Singleton реестр сериализаторов.

    Позволяет регистрировать сериализаторы и выполнять
    экспорт/импорт в правильном порядке зависимостей.
    """

    _instance: Optional["SaveableRegistry"] = None
    _serializers: Dict[str, Type[Saveable]]
    _initialized: bool

    def __new__(cls) -> "SaveableRegistry":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._serializers = {}
            cls._instance._initialized = False
        return cls._instance

    def _ensure_initialized(self) -> None:
        """Ленивая инициализация сериализаторов."""
        if not self._initialized:
            self._initialized = True
            from app.services.persistence.serializers import register_all
            register_all(self)

    def register(self, serializer_class: Type[Saveable]) -> Type[Saveable]:
        """Зарегистрировать сериализатор.

        Использование:
            registry.register(PlayerSerializer)
        """
        name = serializer_class.entity_name()
        if name in self._serializers:
            return serializer_class  # Уже зарегистрирован
        self._serializers[name] = serializer_class
        return serializer_class

    def get(self, entity_name: str) -> Type[Saveable]:
        """Получить сериализатор по имени сущности."""
        self._ensure_initialized()
        if entity_name not in self._serializers:
            raise KeyError(f"No serializer registered for: {entity_name}")
        return self._serializers[entity_name]

    def all_names(self) -> List[str]:
        """Получить все зарегистрированные имена сущностей."""
        self._ensure_initialized()
        return list(self._serializers.keys())

    def get_export_order(self) -> List[str]:
        """Получить порядок экспорта с учётом зависимостей.

        Сущности без зависимостей идут первыми.
        """
        self._ensure_initialized()
        return self._topological_sort()

    def get_import_order(self) -> List[str]:
        """Получить порядок импорта (такой же как экспорт)."""
        self._ensure_initialized()
        return self._topological_sort()

    def _topological_sort(self) -> List[str]:
        """Топологическая сортировка по зависимостям."""
        visited: set = set()
        result: List[str] = []

        def visit(name: str) -> None:
            if name in visited:
                return
            visited.add(name)

            serializer = self._serializers.get(name)
            if serializer:
                for dep in serializer.dependencies():
                    if dep in self._serializers:
                        visit(dep)

            result.append(name)

        for name in self._serializers:
            visit(name)

        return result

    def export_all(self, context: ExportContext) -> Dict[str, Any]:
        """Экспортировать все сущности в словарь.

        Возвращает:
            {
                "entity_name": {
                    "version": 1,
                    "data": [...]
                },
                ...
            }
        """
        self._ensure_initialized()
        entities: Dict[str, Any] = {}

        for name in self.get_export_order():
            serializer = self._serializers[name]
            data = serializer.export(context)
            entities[name] = {
                "version": serializer.version(),
                "data": data
            }
            context.set_exported(name, data)

        return entities

    def import_all(
        self,
        entities_data: Dict[str, Any],
        context: ImportContext
    ) -> Dict[str, int]:
        """Импортировать все сущности из словаря.

        Возвращает количество созданных записей по каждой сущности.
        """
        self._ensure_initialized()
        counts: Dict[str, int] = {}

        for name in self.get_import_order():
            if name not in entities_data:
                continue

            serializer = self._serializers[name]
            entity_info = entities_data[name]
            data = entity_info.get("data", [])

            if context.validation_only:
                serializer.validate(data, context)
                counts[name] = len(data)
            else:
                count = serializer.import_(data, context)
                counts[name] = count

        return counts

    def validate_all(
        self,
        entities_data: Dict[str, Any],
        context: ImportContext
    ) -> None:
        """Валидировать все сущности без импорта."""
        self._ensure_initialized()
        context.validation_only = True

        for name in self.get_import_order():
            if name not in entities_data:
                continue

            serializer = self._serializers[name]
            entity_info = entities_data[name]
            data = entity_info.get("data", [])

            serializer.validate(data, context)


# Глобальный экземпляр реестра
registry = SaveableRegistry()
