import json
import logging
from datetime import date, timedelta
from pathlib import Path

from sqlalchemy.orm import Session

from ect_app.models.document import Document
from ect_app.models.entity import Entity
from ect_app.models.filing import FilingDeadline
from ect_app.models.officer import OfficerDirector
from ect_app.models.relationship import EntityRelationship

logger = logging.getLogger(__name__)

SAMPLE_DIR = Path(__file__).parent.parent.parent / "data" / "sample"


def _offset_to_date(offset_days: int) -> date:
    return date.today() + timedelta(days=offset_days)


def seed_sample_data(db: Session) -> bool:
    """Load sample data if the database is empty. Returns True if seeded."""
    existing = db.query(Entity).count()
    if existing > 0:
        logger.info("Database already has %d entities — skipping seed.", existing)
        return False

    entities_file = SAMPLE_DIR / "entities.json"
    relationships_file = SAMPLE_DIR / "relationships.json"

    if not entities_file.exists():
        logger.warning("Sample data file not found: %s", entities_file)
        return False

    with open(entities_file) as f:
        entities_data = json.load(f)

    # Create entities and track name -> id mapping
    name_to_entity: dict[str, Entity] = {}

    for edata in entities_data:
        entity = Entity(
            name=edata["name"],
            jurisdiction=edata["jurisdiction"],
            entity_type=edata["entity_type"],
            formation_date=_offset_to_date(edata.get("formation_date_offset", -365)),
            registered_agent_name=edata.get("registered_agent_name"),
            registered_agent_address=edata.get("registered_agent_address"),
            good_standing=edata.get("good_standing", True),
            notes=edata.get("notes"),
        )
        db.add(entity)
        db.flush()  # Get the ID
        name_to_entity[entity.name] = entity

        # Officers
        for odata in edata.get("officers", []):
            officer = OfficerDirector(
                entity_id=entity.id,
                name=odata["name"],
                title=odata["title"],
                role=odata["role"],
                term_start=_offset_to_date(odata.get("term_start_offset", -365)),
                term_end=(
                    _offset_to_date(odata["term_end_offset"])
                    if odata.get("term_end_offset") else None
                ),
                email=odata.get("email"),
            )
            db.add(officer)

        # Filings
        for fdata in edata.get("filings", []):
            filing = FilingDeadline(
                entity_id=entity.id,
                filing_type=fdata["filing_type"],
                jurisdiction=fdata["jurisdiction"],
                due_date=_offset_to_date(fdata["due_date_offset"]),
                status=fdata.get("status", "pending"),
                notes=fdata.get("notes"),
            )
            db.add(filing)

        # Documents
        for ddata in edata.get("documents", []):
            doc = Document(
                entity_id=entity.id,
                title=ddata["title"],
                document_type=ddata["document_type"],
                url=ddata.get("url"),
                description=ddata.get("description"),
            )
            db.add(doc)

    # Relationships
    if relationships_file.exists():
        with open(relationships_file) as f:
            rels_data = json.load(f)

        for rdata in rels_data:
            parent = name_to_entity.get(rdata["parent"])
            child = name_to_entity.get(rdata["child"])
            if parent and child:
                rel = EntityRelationship(
                    parent_id=parent.id,
                    child_id=child.id,
                    relationship_type=rdata.get("relationship_type", "subsidiary"),
                    ownership_percentage=rdata.get("ownership_percentage"),
                )
                db.add(rel)
            else:
                logger.warning(
                    "Relationship skipped — missing entity: parent=%s, child=%s",
                    rdata["parent"], rdata["child"],
                )

    db.commit()
    logger.info("Seeded %d sample entities with relationships.", len(name_to_entity))
    return True
