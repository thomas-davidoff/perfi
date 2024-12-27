import pytest
from app.repositories import (
    TransactionsFileRepository,
    TransactionRepository,
    AccountRepository,
    UserRepository,
)
from app.services import LocalFileService, FileImportService
from werkzeug.datastructures import FileStorage
from io import BytesIO
from uuid import uuid4
from pathlib import Path
import tempfile


MOCK_CSV_ROWS = [
    {
        "AMNT": "100.00",
        "description": "Groceries",
        "merchant": "Walmart",
        "date": "2024-01-01",
        "category": "groceries",
    },
    {
        "AMNT": "50.00",
        "description": "Transportation",
        "merchant": "Uber",
        "date": "2024-01-02",
        "category": "transportation",
    },
]


@pytest.fixture
def mock_file():
    file_content = ",".join(MOCK_CSV_ROWS[0].keys())
    for row in MOCK_CSV_ROWS:
        file_content += "\n" + ",".join(row.values())
    return FileStorage(
        stream=BytesIO(file_content.encode("utf-8")),
        filename="test_file.csv",
        content_type="text/csv",
    )


@pytest.fixture
def mock_user_id():
    return str(uuid4())


@pytest.fixture
def mock_account_and_user_ids(valid_account):
    return valid_account.id, valid_account.user_id


@pytest.fixture
def test_upload_folder():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def file_import_service(test_upload_folder):
    file_service = LocalFileService(upload_folder=test_upload_folder)
    transaction_repo = TransactionRepository()
    transaction_file_repo = TransactionsFileRepository()
    account_repo = AccountRepository()
    user_repo = UserRepository()
    return FileImportService(
        file_service=file_service,
        transaction_repo=transaction_repo,
        file_repo=transaction_file_repo,
        account_repo=account_repo,
        user_repo=user_repo,
    )


def test_save_and_preview(file_import_service, mock_file, mock_account_and_user_ids):

    account_id, user_id = mock_account_and_user_ids
    file_record, headers = file_import_service.save_and_preview(
        file=mock_file, user_id=user_id, account_id=account_id
    )

    assert file_record is not None
    assert file_record.status == "PENDING"
    assert headers == list(MOCK_CSV_ROWS[0].keys())
    assert file_record.preview_data == MOCK_CSV_ROWS


def test_map_headers(file_import_service, mock_file, mock_account_and_user_ids):

    account_id, user_id = mock_account_and_user_ids
    file_record, headers = file_import_service.save_and_preview(
        file=mock_file, user_id=user_id, account_id=account_id
    )

    mapped_headers = {
        "AMNT": "amount",
        "description": "description",
        "merchant": "merchant",
        "date": "date",
        "category": "category",
    }
    file_import_service.map_headers(file_record.id, mapped_headers)

    updated_file = file_import_service.file_repo.get_by_id(file_record.id)
    assert updated_file.mapped_headers == mapped_headers
    assert updated_file.status == "VALIDATED"


def test_import_transactions(
    file_import_service,
    mock_file,
    mock_account_and_user_ids,
):
    account_id, user_id = mock_account_and_user_ids
    file_record, headers = file_import_service.save_and_preview(
        file=mock_file, user_id=user_id, account_id=account_id
    )

    # Step 2: Map headers
    mapped_headers = {
        "AMNT": "amount",
        "description": "description",
        "merchant": "merchant",
        "date": "date",
        "category": "category",
    }

    file_import_service.map_headers(file_record.id, mapped_headers)

    # Step 3: Import transactions
    file_import_service.import_transactions(file_record.id)

    # Check that the file status is updated to "IMPORTED"
    updated_file = file_import_service.file_repo.get_by_id(file_record.id)
    assert updated_file.status == "IMPORTED"

    # Verify transactions are created
    transactions = file_import_service.transaction_repo.get_all()
    assert len(transactions) == 2
    assert transactions[0].amount == 100.00
    assert transactions[0].description == "Groceries"
    assert transactions[0].merchant == "Walmart"
    assert transactions[0].date.strftime("%Y-%m-%d") == "2024-01-01"
    assert transactions[0].category == "groceries"
