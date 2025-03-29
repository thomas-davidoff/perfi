from pydantic import (
    ConfigDict,
    Field,
    model_serializer,
    BaseModel,
    field_serializer,
    BeforeValidator,
)
from typing import Optional, Dict, Any, List, Literal, Annotated, OrderedDict
from uuid import UUID
from .generics import Record, GenericResponse
from .transaction import TransactionFields
import json
import enum


class TransactionsFileImportStatus(enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    VALIDATED = "VALIDATED"
    IMPORTED = "IMPORTED"
    FAILED = "FAILED"


convert_to_json = lambda t: json.loads(t) if t is not None else None


preview_data_pre_validate = Annotated[
    Optional[List[Dict[str, Any]]],
    BeforeValidator(convert_to_json),
]

errors_pre_validate = Annotated[
    Optional[List[str]],
    BeforeValidator(convert_to_json),
]

mapped_headers_pre_validate = Annotated[
    Optional[Dict[str, str]], BeforeValidator(convert_to_json)
]


class TransactionsFile(Record):
    """
    A full serialized transaction file.
    """

    file_path: str = Field(exclude=True)  # exclude this one

    filename: str
    headers: Optional[List] = Field(default=None)
    user_id: UUID
    status: TransactionsFileImportStatus
    mapped_headers: mapped_headers_pre_validate = None
    error_log: errors_pre_validate = None
    account_id: UUID
    preview_data: preview_data_pre_validate = None

    @field_serializer("headers", when_used="always")
    def get_preview_headers(self, headers: Optional[List]):
        if self.preview_data:
            return list(self.preview_data[0].keys())

    @field_serializer("status")
    def cap_status(self, status: TransactionsFileImportStatus):
        return status.capitalize()

    model_config = ConfigDict(from_attributes=True)


class TransactionFileCompact(TransactionsFile):
    """
    A compact representation of a transaction file
    """

    @model_serializer
    def ser_model(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "filename": self.filename,
            "status": self.status.capitalize(),
        }


class UploadTransactionFileInfo(BaseModel):
    """
    A representation of a file and its headers
    """

    file: TransactionFileCompact
    headers: List[str]


class UploadTransactionFileResponse(GenericResponse):
    """
    A representation of a transaction file response after uploading
    """

    data: UploadTransactionFileInfo


class HeaderMappingRequest(BaseModel):
    """
    Schema for mapping headers from a CSV file to transaction fields.
    """

    mapped_headers: Dict[str, TransactionFields] = Field(
        ...,
        description="A dictionary where keys are file column headers, "
        "and values are valid transaction field names.",
    )
