import logging
from typing import Any, Generic, Type, TypeVar

from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..repositories.base import BaseRepository

ModelT = TypeVar("ModelT")
RepoT = TypeVar("RepoT", bound=BaseRepository)
CreateSchemaT = TypeVar("CreateSchemaT", bound=BaseModel)
UpdateSchemaT = TypeVar("UpdateSchemaT", bound=BaseModel)
ResponseSchemaT = TypeVar("ResponseSchemaT", bound=BaseModel)
ListResponseSchemaT = TypeVar("ListResponseSchemaT", bound=BaseModel)


class BaseService(
    Generic[
        ModelT,
        RepoT,
        CreateSchemaT,
        UpdateSchemaT,
        ResponseSchemaT,
        ListResponseSchemaT,
    ]
):
    """
    Generic base service providing CRUD operations.

    Type Parameters:
        ModelT: SQLAlchemy model class
        RepoT: Repository class for the model
        CreateSchemaT: Pydantic schema for creation
        UpdateSchemaT: Pydantic schema for updates
        ResponseSchemaT: Pydantic schema for single entity response
        ListResponseSchemaT: Pydantic schema for list response
    """

    repository_class: Type[RepoT]
    response_schema: Type[ResponseSchemaT]
    list_response_schema: Type[ListResponseSchemaT]

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = self.repository_class(db)

        self.logger = logging.getLogger(self.__class__.__name__)

    def get(self, pk: Any) -> ResponseSchemaT:
        """Get an entity by primary key."""
        entity = self.repo.get_or_raise(pk)
        return self.response_schema.model_validate(entity)

    def list(self, skip: int = 0, limit: int = 100) -> ListResponseSchemaT:
        """List entities with pagination."""
        entities = self.repo.get_all(skip=skip, limit=limit)
        total = self.repo.count()

        return self.list_response_schema(
            items=[self.response_schema.model_validate(e) for e in entities],
            total=total,
            skip=skip,
            limit=limit,
        )

    def create(self, data: CreateSchemaT) -> ResponseSchemaT:
        """Create a new entity."""
        entity = self.repo.create(data.model_dump())
        self.db.commit()
        self.logger.info(
            f"Created {self.repo.model.__name__}: {getattr(entity, self.repo.pk_field)}"
        )
        return self.response_schema.model_validate(entity)

    def update(self, pk: Any, data: UpdateSchemaT) -> ResponseSchemaT:
        """Update an entity."""
        entity = self.repo.update(pk, data.model_dump(exclude_unset=True))
        self.db.commit()
        self.logger.info(f"Updated {self.repo.model.__name__}: {pk}")
        return self.response_schema.model_validate(entity)

    def has_changes(self, pk: Any, data: UpdateSchemaT) -> bool:
        """
        Check if the update data contains changes compared to existing entity.

        Args:
            pk: Primary key of the entity
            data: Update data to compare

        Returns:
            bool: True if there are changes, False if data is identical
        """
        try:
            entity = self.repo.get(pk)
            if not entity:
                return True

            update_dict = data.model_dump(exclude_unset=True)

            for field, new_value in update_dict.items():
                current_value = getattr(entity, field, None)

                if current_value is None and new_value is None:
                    continue

                if isinstance(current_value, float) and isinstance(new_value, float):
                    if abs(current_value - new_value) > 1e-9:
                        return True
                elif current_value != new_value:
                    return True

            return False

        except Exception as e:
            self.logger.warning(f"Error checking changes for {pk}: {e}")
            return True

    def update_if_changed(
        self, pk: Any, data: UpdateSchemaT
    ) -> tuple[ResponseSchemaT, bool]:
        """
        Update an entity only if the data has changed.

        Args:
            pk: Primary key of the entity
            data: Update data

        Returns:
            tuple: (ResponseSchemaT, bool) - Updated entity and whether update occurred
        """
        if self.has_changes(pk, data):
            entity = self.update(pk, data)
            return entity, True
        else:
            entity = self.get(pk)
            self.logger.debug(
                f"No changes detected for {self.repo.model.__name__}: {pk}"
            )
            return entity, False

    def delete(self, pk: Any) -> bool:
        """Delete an entity."""
        result = self.repo.delete(pk)
        if result:
            self.db.commit()
            self.logger.info(f"Deleted {self.repo.model.__name__}: {pk}")
        return result
