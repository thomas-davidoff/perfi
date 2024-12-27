from app.repositories.repositories import Repository
from uuid import UUID
from database import TransactionsFile
from extensions import db
from sqlalchemy.exc import NoResultFound, IntegrityError
from app.exceptions import AlreadyExistsError


class TransactionsFileRepository(Repository[TransactionsFile]):
    def __init__(self) -> None:
        super().__init__(entity_name="transactions_file_import", model=TransactionsFile)

    def get_by_id(self, id: UUID, user_id: UUID) -> TransactionsFile | None:
        """
        Get a file import record by its ID.

        :param id: The UUID of the file import record.
        :return: The file import record or None if not found.
        """
        entity = (
            db.session.query(TransactionsFile)
            .filter(TransactionsFile.id == id, TransactionsFile.user_id == user_id)
            .one_or_none()
        )
        return entity

    def create(self, data: dict) -> TransactionsFile:
        """
        Create a file import record in the database.

        :param data: Dictionary containing file import details.
        :return: The created file import record.
        """
        try:
            return super().create(data)
        except IntegrityError as e:
            if "violates unique constraint" in str(e):
                raise AlreadyExistsError("Transaction file already exists")
            raise

    def get_by_status(self, status: str) -> list[TransactionsFile]:
        """
        Retrieve all file imports with a specific status.

        :param status: The status of the file imports to retrieve.
        :return: List of file imports with the specified status.
        """
        return (
            db.session.query(TransactionsFile)
            .filter(TransactionsFile.status == status)
            .all()
        )

    def bulk_update_status(self, ids: list[UUID], status: str) -> None:
        """
        Update the status of multiple file imports.

        :param ids: List of file import IDs.
        :param status: New status to set for the file imports.
        """
        db.session.query(TransactionsFile).filter(TransactionsFile.id.in_(ids)).update(
            {"status": status}, synchronize_session="fetch"
        )
        db.session.commit()

    def get_all(self):
        return super().get_all()

    def bulk_delete(self, ids):
        return super().bulk_delete(ids)

    def update(self, id: UUID, data: dict, user_id: UUID):
        """Updates an existing transaction file in the database."""
        file = self.get_by_id(id, user_id=user_id)
        if file is None:
            raise NoResultFound(f"{self.entity_name} with ID {id} does not exist.")
        for key, value in data.items():
            setattr(file, key, value)
        db.session.commit()
        return file

    def get_by_status(self, status: str):
        try:
            return (
                db.session.query(self.model).filter(self.model.status == status).all()
            )
        except NoResultFound:
            return None
