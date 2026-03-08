from sqlalchemy.orm import Session

from ect_app.models.entity import Entity
from ect_app.models.relationship import EntityRelationship
from ect_app.schemas.relationship import RelationshipCreate


def list_relationships(db: Session, entity_id: int) -> dict:
    as_parent = (
        db.query(EntityRelationship)
        .filter(EntityRelationship.parent_id == entity_id)
        .all()
    )
    as_child = (
        db.query(EntityRelationship)
        .filter(EntityRelationship.child_id == entity_id)
        .all()
    )
    return {"children": as_parent, "parents": as_child}


def create_relationship(db: Session, data: RelationshipCreate) -> EntityRelationship:
    # Check for cycles before creating
    if _would_create_cycle(db, data.parent_id, data.child_id):
        raise ValueError("This relationship would create a circular dependency")

    rel = EntityRelationship(**data.model_dump())
    db.add(rel)
    db.commit()
    db.refresh(rel)
    return rel


def delete_relationship(db: Session, relationship_id: int) -> bool:
    rel = db.query(EntityRelationship).filter(EntityRelationship.id == relationship_id).first()
    if not rel:
        return False
    db.delete(rel)
    db.commit()
    return True


def _would_create_cycle(db: Session, parent_id: int, child_id: int) -> bool:
    """Check if making child_id a child of parent_id would create a cycle.

    A cycle exists if parent_id is already a descendant of child_id.
    We check by traversing all descendants of child_id — if parent_id
    is reachable, adding child_id as a child of parent_id would close a loop.
    """
    visited: set[int] = set()
    queue = [child_id]

    while queue:
        current = queue.pop(0)
        if current in visited:
            continue
        visited.add(current)

        if current == parent_id:
            return True

        # Traverse children of current
        child_rels = (
            db.query(EntityRelationship)
            .filter(EntityRelationship.parent_id == current)
            .all()
        )
        for rel in child_rels:
            queue.append(rel.child_id)

    return False


def get_org_tree(db: Session) -> list[dict]:
    """Build D3-compatible hierarchical tree from entity relationships."""
    entities = {e.id: e for e in db.query(Entity).all()}
    relationships = db.query(EntityRelationship).all()

    # Find child IDs (entities that have a parent)
    child_ids = {r.child_id for r in relationships}

    # Build adjacency: parent_id -> list of (child_id, relationship)
    children_map: dict[int, list[EntityRelationship]] = {}
    for rel in relationships:
        children_map.setdefault(rel.parent_id, []).append(rel)

    # Root entities = those not appearing as children
    root_ids = [eid for eid in entities if eid not in child_ids]

    def build_node(entity_id: int, rel: EntityRelationship | None = None) -> dict:
        entity = entities[entity_id]
        node = {
            "name": f"{entity.name} ({entity.jurisdiction})",
            "entity_id": entity.id,
            "entity_type": entity.entity_type,
            "jurisdiction": entity.jurisdiction,
            "good_standing": entity.good_standing,
            "ownership_percentage": rel.ownership_percentage if rel else None,
            "relationship_type": rel.relationship_type if rel else None,
            "children": [],
        }
        for child_rel in children_map.get(entity_id, []):
            if child_rel.child_id in entities:
                node["children"].append(build_node(child_rel.child_id, child_rel))
        return node

    roots = [build_node(rid) for rid in sorted(root_ids)]

    # If multiple roots, wrap in a virtual portfolio node
    if len(roots) > 1:
        return [{
            "name": "Corporate Portfolio",
            "entity_id": 0,
            "entity_type": "portfolio",
            "jurisdiction": "",
            "good_standing": True,
            "ownership_percentage": None,
            "relationship_type": None,
            "children": roots,
        }]

    return roots
