from abc import abstractmethod
from typing import List
from sqlalchemy.exc import NoResultFound
from app import logger
from extensions import db


class Repository:
    def __init__(self, model, model_name) -> None:
        self.model = model
        self.name = model_name
        pass

    @abstractmethod
    def create(self, data):
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, id):
        raise NotImplementedError

    @abstractmethod
    def update(self, id, data):
        raise NotImplementedError

    def delete(self, id) -> int:
        f"""Deletes a {self.name} by ID"""
        instance = self.get_by_id(id)
        if instance:
            db.session.delete(instance)
            db.session.commit()
            return id
        else:
            logger.error(f"No {self.name} with ID {id} exists.")
            raise NoResultFound(f"No {self.name} with ID {id} exists.")

    @abstractmethod
    def bulk_delete(self, ids: List[int]):
        raise NotImplementedError
