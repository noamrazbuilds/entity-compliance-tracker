from sqlalchemy.orm import Session

from ect_app.models.document import Document
from ect_app.schemas.document import DocumentCreate, DocumentUpdate


def list_documents(db: Session, entity_id: int) -> list[Document]:
    return (
        db.query(Document)
        .filter(Document.entity_id == entity_id)
        .order_by(Document.title)
        .all()
    )


def get_document(db: Session, document_id: int) -> Document | None:
    return db.query(Document).filter(Document.id == document_id).first()


def create_document(db: Session, entity_id: int, data: DocumentCreate) -> Document:
    doc = Document(entity_id=entity_id, **data.model_dump())
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


def update_document(db: Session, document_id: int, data: DocumentUpdate) -> Document | None:
    doc = get_document(db, document_id)
    if not doc:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(doc, key, value)
    db.commit()
    db.refresh(doc)
    return doc


def delete_document(db: Session, document_id: int) -> bool:
    doc = get_document(db, document_id)
    if not doc:
        return False
    db.delete(doc)
    db.commit()
    return True
