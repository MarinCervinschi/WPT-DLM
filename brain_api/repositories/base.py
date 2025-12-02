import logging
from typing import Any, Generic, List, Sequence, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

ModelT = TypeVar("ModelT")
CreateSchemaT = TypeVar("CreateSchemaT")
UpdateSchemaT = TypeVar("UpdateSchemaT")


class RepositoryError(Exception):
    """Base exception for repository operations."""

    pass


class NotFoundError(RepositoryError):
    """Raised when an entity is not found."""

    pass


class DuplicateError(RepositoryError):
    """Raised when attempting to create a duplicate entity."""

    pass


class BaseRepository(Generic[ModelT, CreateSchemaT, UpdateSchemaT]):
    """
    Generic base repository providing CRUD operations.

    Type Parameters:
        ModelT: SQLAlchemy model class
        CreateSchemaT: Pydantic schema for creation
        UpdateSchemaT: Pydantic schema for updates
    """

    model: Type[ModelT]
    pk_field: str = "id"

    def __init__(self, db: Session) -> None:
        """
        Initialize repository with database session.

        Args:
            db: SQLAlchemy session
        """
        self.db = db

    # ==================== READ OPERATIONS ====================

    def get(self, pk: Any) -> ModelT | None:
        """
        Get a single entity by primary key.

        Args:
            pk: Primary key value

        Returns:
            Entity or None if not found
        """
        return self.db.get(self.model, pk)

    def get_or_raise(self, pk: Any) -> ModelT:
        """
        Get a single entity by primary key, raising if not found.

        Args:
            pk: Primary key value

        Returns:
            Entity

        Raises:
            NotFoundError: If entity not found
        """
        entity = self.get(pk)
        if entity is None:
            raise NotFoundError(
                f"{self.model.__name__} with {self.pk_field}={pk} not found"
            )
        return entity

    def get_by_field(self, field: str, value: Any) -> ModelT | None:
        """
        Get a single entity by any field.

        Args:
            field: Field name to filter by
            value: Value to match

        Returns:
            Entity or None if not found
        """
        stmt = select(self.model).where(getattr(self.model, field) == value)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_all(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        order_by: str | None = None,
        descending: bool = False,
    ) -> Sequence[ModelT]:
        """
        Get all entities with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            order_by: Field name to order by
            descending: Sort in descending order

        Returns:
            List of entities
        """
        stmt = select(self.model)

        if order_by:
            order_field = getattr(self.model, order_by)
            stmt = stmt.order_by(order_field.desc() if descending else order_field)

        stmt = stmt.offset(skip).limit(limit)
        return self.db.execute(stmt).scalars().all()

    def filter_by(self, **kwargs: Any) -> Sequence[ModelT]:
        """
        Filter entities by field values.

        Args:
            **kwargs: Field-value pairs to filter by

        Returns:
            List of matching entities
        """
        stmt = select(self.model).filter_by(**kwargs)
        return self.db.execute(stmt).scalars().all()

    def count(self, **kwargs: Any) -> int:
        """
        Count entities, optionally filtered by field values.

        Args:
            **kwargs: Field-value pairs to filter by

        Returns:
            Count of matching entities
        """
        from sqlalchemy import func

        stmt = select(func.count()).select_from(self.model)
        if kwargs:
            stmt = stmt.filter_by(**kwargs)
        return self.db.execute(stmt).scalar_one()

    def exists(self, pk: Any) -> bool:
        """
        Check if an entity exists by primary key.

        Args:
            pk: Primary key value

        Returns:
            True if entity exists
        """
        return self.get(pk) is not None

    # ==================== CREATE OPERATIONS ====================

    def create(self, data: dict[str, Any] | CreateSchemaT) -> ModelT:
        """
        Create a new entity.

        Args:
            data: Dictionary or Pydantic schema with entity data

        Returns:
            Created entity

        Raises:
            DuplicateError: If entity with same PK already exists
        """
        if hasattr(data, "model_dump"):
            data = data.model_dump(exclude_unset=True)  # type: ignore[union-attr]

        try:
            entity = self.model(**data)  # type: ignore[call-arg]
            self.db.add(entity)
            self.db.flush()
            self.db.refresh(entity)
            logger.debug(f"Created {self.model.__name__}: {entity}")
            return entity
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Integrity error creating {self.model.__name__}: {e}")
            raise DuplicateError(f"Entity already exists or constraint violation: {e}")

    def create_many(self, items: List[dict[str, Any] | CreateSchemaT]) -> List[ModelT]:
        """
        Create multiple entities in batch.

        Args:
            items: List of dictionaries or Pydantic schemas

        Returns:
            List of created entities
        """
        entities = []
        for item in items:
            if hasattr(item, "model_dump"):
                item = item.model_dump(exclude_unset=True)  # type: ignore[union-attr]
            entities.append(self.model(**item))  # type: ignore[call-arg]

        try:
            self.db.add_all(entities)
            self.db.flush()
            for entity in entities:
                self.db.refresh(entity)
            logger.debug(f"Created {len(entities)} {self.model.__name__} entities")
            return entities
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Integrity error in batch create: {e}")
            raise DuplicateError(f"Batch insert failed: {e}")

    def get_or_create(
        self, pk: Any, defaults: dict[str, Any] | None = None
    ) -> tuple[ModelT, bool]:
        """
        Get existing entity or create new one.

        Args:
            pk: Primary key value
            defaults: Default values for creation

        Returns:
            Tuple of (entity, created) where created is True if new
        """
        entity = self.get(pk)
        if entity:
            return entity, False

        data = {self.pk_field: pk, **(defaults or {})}
        return self.create(data), True

    # ==================== UPDATE OPERATIONS ====================

    def update(self, pk: Any, data: dict[str, Any] | UpdateSchemaT) -> ModelT:
        """
        Update an existing entity.

        Args:
            pk: Primary key value
            data: Dictionary or Pydantic schema with update data

        Returns:
            Updated entity

        Raises:
            NotFoundError: If entity not found
        """
        entity = self.get_or_raise(pk)

        if hasattr(data, "model_dump"):
            data = data.model_dump(exclude_unset=True)  # type: ignore[union-attr]

        for field, value in data.items():  # type: ignore[union-attr]
            if hasattr(entity, field):
                setattr(entity, field, value)

        try:
            self.db.flush()
            self.db.refresh(entity)
            logger.debug(f"Updated {self.model.__name__}: {entity}")
            return entity
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error updating {self.model.__name__}: {e}")
            raise RepositoryError(f"Update failed: {e}")

    def update_by_field(
        self, field: str, value: Any, data: dict[str, Any]
    ) -> Sequence[ModelT]:
        """
        Update multiple entities matching a field value.

        Args:
            field: Field name to filter by
            value: Value to match
            data: Update data

        Returns:
            List of updated entities
        """
        entities = self.filter_by(**{field: value})
        for entity in entities:
            for k, v in data.items():
                if hasattr(entity, k):
                    setattr(entity, k, v)

        self.db.flush()
        return entities

    def upsert(self, pk: Any, data: dict[str, Any]) -> tuple[ModelT, bool]:
        """
        Update if exists, create if not.

        Args:
            pk: Primary key value
            data: Entity data

        Returns:
            Tuple of (entity, created) where created is True if new
        """
        entity = self.get(pk)
        if entity:
            return self.update(pk, data), False

        data[self.pk_field] = pk
        return self.create(data), True

    # ==================== DELETE OPERATIONS ====================

    def delete(self, pk: Any) -> bool:
        """
        Delete an entity by primary key.

        Args:
            pk: Primary key value

        Returns:
            True if deleted, False if not found
        """
        entity = self.get(pk)
        if entity is None:
            return False

        try:
            self.db.delete(entity)
            self.db.flush()
            logger.debug(f"Deleted {self.model.__name__} with {self.pk_field}={pk}")
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error deleting {self.model.__name__}: {e}")
            raise RepositoryError(f"Delete failed: {e}")

    def delete_or_raise(self, pk: Any) -> None:
        """
        Delete an entity, raising if not found.

        Args:
            pk: Primary key value

        Raises:
            NotFoundError: If entity not found
        """
        if not self.delete(pk):
            raise NotFoundError(
                f"{self.model.__name__} with {self.pk_field}={pk} not found"
            )

    def delete_many(self, pks: list[Any]) -> int:
        """
        Delete multiple entities by primary keys.

        Args:
            pks: List of primary key values

        Returns:
            Number of deleted entities
        """
        deleted = 0
        for pk in pks:
            if self.delete(pk):
                deleted += 1
        return deleted

    def delete_by_field(self, field: str, value: Any) -> int:
        """
        Delete all entities matching a field value.

        Args:
            field: Field name to filter by
            value: Value to match

        Returns:
            Number of deleted entities
        """
        entities = self.filter_by(**{field: value})
        for entity in entities:
            self.db.delete(entity)
        self.db.flush()
        return len(entities)