from abc import abstractmethod, ABC
from typing import List
from sqlalchemy.exc import NoResultFound, IntegrityError
from app import logger
from extensions import db
from typing import TypeVar, Generic


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
        user = db.session.query(self.model).filter(self.model.id == id).one_or_none()
        if user is None:
            logger.error(f"No user with ID {id} exists.")
            raise NoResultFound("No user with ID {id} exists.")
        return user

    def delete(self, id) -> int:
        f"""Deletes an entity by ID"""
        instance = self.get_by_id(id)
        if instance:
            db.session.delete(instance)
            db.session.commit()
            return id
        else:
            logger.error(f"No {self.entity_name} with ID {id} exists.")
            raise NoResultFound(f"No {self.entity_name} with ID {id} exists.")

    @abstractmethod
    def bulk_delete(self, ids: List[int]) -> List[int]:
        pass

    @abstractmethod
    def update(self, id: int, data: dict) -> T:
        """Updates an existing entity in the database."""
        user = self.get_by_id(id)
        for key, value in data.items():
            setattr(user, key, value)
        db.session.commit()
        return user
