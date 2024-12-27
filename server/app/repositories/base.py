from abc import abstractmethod, ABC
from typing import List
from sqlalchemy.exc import NoResultFound, IntegrityError, ArgumentError
from app import logger
from extensions import db
from typing import TypeVar, Generic
from uuid import UUID
from app.exceptions import ResourceNotFoundError
from app.validators import to_uuid


T = TypeVar("T")


class Repository(ABC, Generic[T]):
    def __init__(self, entity_name, model) -> None:
        self.entity_name = entity_name
        self.model = model

    @abstractmethod
    def create(self, data: dict) -> T:
        """Creates an entity of entity T."""
        entity = self.model(**data)
        db.session.add(entity)
        try:
            db.session.commit()
            return entity
        except IntegrityError:
            logger.error(f"Integrity error when attempting to create {entity}")
            db.session.rollback()
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e} when attempting to create {entity}")
            db.session.rollback()
            raise

    @abstractmethod
    def get_by_id(self, id: int) -> T | None:
        """
        Gets an entity by ID

        :param id:
            The id of the entity
        :return entity:
            entity instance or None
        """
        uuid = to_uuid(id)
        entity = (
            db.session.query(self.model).filter(self.model.id == uuid).one_or_none()
        )
        return entity

    @abstractmethod
    def get_all(self) -> List[T]:
        """Gets all entities"""
        return db.session.query(self.model).all()

    def delete(self, id: int) -> int:
        f"""Deletes an entity by ID"""
        uuid = to_uuid(id)
        instance = self.get_by_id(uuid)
        if instance:
            db.session.delete(instance)
            db.session.commit()
            return uuid
        else:
            logger.error(f"No {self.entity_name} with ID {id} exists.")
            raise ResourceNotFoundError(f"No {self.entity_name} with ID {id} exists.")

    @abstractmethod
    def bulk_delete(self, ids: List[int]) -> List[int]:
        pass

    @abstractmethod
    def update(self, id: int, data: dict) -> T:
        """Updates an existing entity in the database."""
        uuid = to_uuid(id)
        user = self.get_by_id(uuid)
        if user is None:
            raise ResourceNotFoundError(
                f"{self.entity_name} with ID {uuid} does not exist."
            )
        for key, value in data.items():
            setattr(user, key, value)
        db.session.commit()
        return user
