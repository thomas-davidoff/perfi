from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from perfi.schemas import (
    GenericResponse,
    TransactionsFile,
    UploadTransactionFileResponse,
    HeaderMappingRequest,
)
from perfi.services.file_import import FileImportService
from perfi.core.dependencies.current_user import get_current_user
from perfi.core.dependencies.service_factories import get_file_import_service
from perfi.core.dependencies.session import get_async_session
from perfi.core.dependencies.resource_ownership import (
    get_validated_account,
    get_validated_transactions_file,
)
from perfi.core.database import Account as AccountDBModel
from uuid import UUID


router = APIRouter(prefix="/files", tags=["File Imports"])


@router.post("/upload", response_model=UploadTransactionFileResponse)
async def upload_file(
    file: UploadFile,
    account: AccountDBModel = Depends(get_validated_account),
    session: AsyncSession = Depends(get_async_session),
    file_import_service: FileImportService = Depends(get_file_import_service),
    current_user=Depends(get_current_user),
) -> UploadTransactionFileResponse:
    """
    Upload a file and preview its contents.
    """
    file_info = await file_import_service.save_and_preview(
        session=session, file=file, user=current_user, account=account
    )
    return UploadTransactionFileResponse(data=file_info)


@router.get("/", response_model=GenericResponse)
async def list_files(
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
    file_import_service: FileImportService = Depends(get_file_import_service),
) -> GenericResponse:
    """
    List all files uploaded by the current user.
    """
    files = await file_import_service.get_user_files(session, user=current_user)
    return GenericResponse(data=[TransactionsFile.model_validate(f) for f in files])


@router.get("/{file_id}", response_model=GenericResponse)
async def get_file_metadata(
    file_id: UUID,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
    file_import_service: FileImportService = Depends(get_file_import_service),
) -> GenericResponse:
    """
    Retrieve metadata for a specific file.
    """
    metadata = await file_import_service.get_file_metadata(
        session, user_id=current_user.id, file_id=file_id
    )
    return GenericResponse(data=metadata)


@router.post("/map-headers/{file_id}", response_model=GenericResponse)
async def map_headers(
    mapping_request: HeaderMappingRequest,
    transactions_file: TransactionsFile = Depends(get_validated_transactions_file),
    session: AsyncSession = Depends(get_async_session),
    file_import_service: FileImportService = Depends(get_file_import_service),
) -> GenericResponse:
    """
    Map file headers to transaction fields.
    """
    file_record = await file_import_service.map_headers(
        session,
        file_record=transactions_file,
        mapped_headers=mapping_request.mapped_headers,
        user_id=transactions_file.user_id,
    )
    return GenericResponse(
        data={
            **{"message": "Headers mapped successfully"},
            **TransactionsFile.model_validate(file_record).model_dump(
                include=["mapped_headers", "status"]
            ),
        }
    )


@router.post("/import/{file_id}", response_model=GenericResponse)
async def import_transactions(
    transactions_file: TransactionsFile = Depends(get_validated_transactions_file),
    session: AsyncSession = Depends(get_async_session),
    file_import_service: FileImportService = Depends(get_file_import_service),
) -> GenericResponse:
    """
    Import transactions from a file into the database.
    """
    result = await file_import_service.import_transactions(
        session, file_record=transactions_file
    )
    return GenericResponse(data=result)
