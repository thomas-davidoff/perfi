from app.repositories.repositories import Repository
from uuid import UUID
from database import TransactionsFileImport
from extensions import db


class TransactionsFileImportRepository(Repository[TransactionsFileImport]):
    def __init__(self) -> None:
        super().__init__(
            entity_name="transactions_file_import", model=TransactionsFileImport
        )

    def get_by_id(self, id: UUID) -> TransactionsFileImport | None:
        """
        Get a file import record by its ID.

        :param id: The UUID of the file import record.
        :return: The file import record or None if not found.
        """
        return super().get_by_id(id)

    def create(self, data: dict) -> TransactionsFileImport:
        """
        Create a file import record in the database.

        :param data: Dictionary containing file import details.
        :return: The created file import record.
        """
        return super().create(data)

    def get_by_status(self, status: str) -> list[TransactionsFileImport]:
        """
        Retrieve all file imports with a specific status.

        :param status: The status of the file imports to retrieve.
        :return: List of file imports with the specified status.
        """
        return (
            db.session.query(TransactionsFileImport)
            .filter(TransactionsFileImport.status == status)
            .all()
        )

    def bulk_update_status(self, ids: list[UUID], status: str) -> None:
        """
        Update the status of multiple file imports.

        :param ids: List of file import IDs.
        :param status: New status to set for the file imports.
        """
        db.session.query(TransactionsFileImport).filter(
            TransactionsFileImport.id.in_(ids)
        ).update({"status": status}, synchronize_session="fetch")
        db.session.commit()

    def get_all(self):
        return super().get_all()

    def bulk_delete(self, ids):
        return super().bulk_delete(ids)

    def update(self, id, data):
        return super().update(id, data)
