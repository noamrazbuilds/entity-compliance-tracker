from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ect_app.database import get_db
from ect_app.schemas.document import DocumentCreate, DocumentRead, DocumentUpdate
from ect_app.services import document_service

router = APIRouter(tags=["documents"])


@router.get("/api/entities/{entity_id}/documents", response_model=list[DocumentRead])
def list_documents(entity_id: int, db: Session = Depends(get_db)) -> list[DocumentRead]:
    return document_service.list_documents(db, entity_id)


@router.post(
    "/api/entities/{entity_id}/documents", response_model=DocumentRead, status_code=201
)
def create_document(
    entity_id: int, data: DocumentCreate, db: Session = Depends(get_db)
) -> DocumentRead:
    return document_service.create_document(db, entity_id, data)


@router.put("/api/documents/{document_id}", response_model=DocumentRead)
def update_document(
    document_id: int, data: DocumentUpdate, db: Session = Depends(get_db)
) -> DocumentRead:
    doc = document_service.update_document(db, document_id, data)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.delete("/api/documents/{document_id}", status_code=204)
def delete_document(document_id: int, db: Session = Depends(get_db)) -> None:
    if not document_service.delete_document(db, document_id):
        raise HTTPException(status_code=404, detail="Document not found")
