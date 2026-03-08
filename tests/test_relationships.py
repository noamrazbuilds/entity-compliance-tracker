def _create_entity(client, name="Test Corp"):
    resp = client.post("/api/entities/", json={
        "name": name, "jurisdiction": "DE", "entity_type": "corporation",
    })
    return resp.json()["id"]


def test_create_relationship(client):
    parent_id = _create_entity(client, "Parent Corp")
    child_id = _create_entity(client, "Child LLC")

    resp = client.post("/api/relationships/", json={
        "parent_id": parent_id,
        "child_id": child_id,
        "relationship_type": "subsidiary",
        "ownership_percentage": 100.0,
    })
    assert resp.status_code == 201
    assert resp.json()["parent_id"] == parent_id
    assert resp.json()["child_id"] == child_id


def test_self_relationship_rejected(client):
    entity_id = _create_entity(client)
    resp = client.post("/api/relationships/", json={
        "parent_id": entity_id,
        "child_id": entity_id,
        "relationship_type": "subsidiary",
    })
    assert resp.status_code == 422  # Pydantic validation error


def test_cycle_detection(client):
    a = _create_entity(client, "A Corp")
    b = _create_entity(client, "B Corp")
    c = _create_entity(client, "C Corp")

    # A -> B -> C
    client.post("/api/relationships/", json={
        "parent_id": a, "child_id": b, "relationship_type": "subsidiary",
    })
    client.post("/api/relationships/", json={
        "parent_id": b, "child_id": c, "relationship_type": "subsidiary",
    })

    # C -> A would create cycle
    resp = client.post("/api/relationships/", json={
        "parent_id": c, "child_id": a, "relationship_type": "subsidiary",
    })
    assert resp.status_code == 400
    assert "circular" in resp.json()["detail"].lower()


def test_org_tree(client):
    parent_id = _create_entity(client, "Parent Corp")
    child_id = _create_entity(client, "Child LLC")
    client.post("/api/relationships/", json={
        "parent_id": parent_id,
        "child_id": child_id,
        "relationship_type": "subsidiary",
        "ownership_percentage": 100.0,
    })

    resp = client.get("/api/relationships/org-tree")
    assert resp.status_code == 200
    tree = resp.json()
    assert len(tree) == 1
    assert tree[0]["entity_id"] == parent_id
    assert len(tree[0]["children"]) == 1
    assert tree[0]["children"][0]["entity_id"] == child_id


def test_org_tree_empty(client):
    resp = client.get("/api/relationships/org-tree")
    assert resp.status_code == 200
    assert resp.json() == []


def test_delete_relationship(client):
    parent_id = _create_entity(client, "Parent Corp")
    child_id = _create_entity(client, "Child LLC")
    resp = client.post("/api/relationships/", json={
        "parent_id": parent_id,
        "child_id": child_id,
        "relationship_type": "subsidiary",
    })
    rel_id = resp.json()["id"]

    resp = client.delete(f"/api/relationships/{rel_id}")
    assert resp.status_code == 204
