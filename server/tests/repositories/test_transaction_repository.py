import pytest
from flask import Flask
from database import User
from app.repositories import UserRepository
from sqlalchemy.exc import IntegrityError, NoResultFound


user_repository = UserRepository()


def test_get_all(app: Flask):
    with app.app_context():
        # Case: Returns a list of transaction objects when transactions exist
        # Case: Returns an empty list when no transactions exist
        pass


def test_get_by_id(app: Flask):
    with app.app_context():
        # Case: Returns a transaction object when the transaction with the given ID exists
        # Case: Raises NoResultFound when the ID does not exist
        # Edge Case: Handling of invalid or non-integer ID input (e.g., a string or special characters)
        # Edge Case: Handling when the ID is a valid integer but outside the possible range of IDs
        pass


def test_get_within_dates(app: Flask):
    with app.app_context():
        # Case: Returns transactions that fall within the given date range
        # Case: Returns an empty list if no transactions fall within the date range
        # Edge Case: Start date and end date are the same, check if transactions on that date are included
        # Edge Case: Start date is after the end date (should return an error or empty result)
        # Edge Case: Dates provided in different formats (e.g., ISO, string, datetime object)
        pass


def test_create(app: Flask):
    with app.app_context():
        # Case: Successfully creates a transaction and returns the transaction object
        # Case: Raises IntegrityError when a duplicate transaction (same ID) is inserted
        # Case: Raises IntegrityError if required fields (e.g., amount, date) are missing
        # Edge Case: Invalid data types for fields (e.g., amount is a string, date is invalid)
        # Edge Case: Extremely large or small transaction amounts (e.g., 0 or very high amounts)
        # Edge Case: Handling of transactions in different currencies (if applicable)
        pass


def test_delete(app: Flask):
    with app.app_context():
        # Case: Successfully deletes a transaction when a valid transaction ID is provided
        # Case: Raises NoResultFound when trying to delete a transaction with a non-existent ID
        # Edge Case: Deleting a transaction that is linked to another entity (e.g., an invoice or a report)
        # Edge Case: Deleting an already deleted or soft-deleted transaction (if applicable)
        pass


def test_update(app: Flask):
    with app.app_context():
        # Case: Successfully updates the transaction and returns the updated transaction object
        # Case: Raises NoResultFound when trying to update a transaction with a non-existent ID
        # Edge Case: Partial updates (only updating one field like `amount` without affecting others)
        # Edge Case: Trying to update a field with an invalid value (e.g., negative transaction amount)
        # Edge Case: Attempt to update read-only fields (if any, such as creation date)
        pass
