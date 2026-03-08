def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


def test_create_and_get_entity(client):
    data = {
        "name": "Acme Corp",
        "jurisdiction": "DE",
        "entity_type": "corporation",
        "formation_date": "2020-01-15",
        "good_standing": True,
    }
    resp = client.post("/api/entities/", json=data)
    assert resp.status_code == 201
    entity = resp.json()
    assert entity["name"] == "Acme Corp"
    assert entity["jurisdiction"] == "DE"

    # Get by ID
    resp = client.get(f"/api/entities/{entity['id']}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Acme Corp"


def test_list_entities(client):
    for name in ["Alpha Inc", "Beta LLC", "Gamma LP"]:
        client.post("/api/entities/", json={
            "name": name, "jurisdiction": "DE", "entity_type": "corporation",
        })
    resp = client.get("/api/entities/")
    assert resp.status_code == 200
    assert len(resp.json()) == 3


def test_list_entities_filter(client):
    client.post("/api/entities/", json={
        "name": "DE Corp", "jurisdiction": "DE", "entity_type": "corporation",
    })
    client.post("/api/entities/", json={
        "name": "CA LLC", "jurisdiction": "CA", "entity_type": "llc",
    })

    resp = client.get("/api/entities/", params={"jurisdiction": "DE"})
    assert len(resp.json()) == 1
    assert resp.json()[0]["jurisdiction"] == "DE"

    resp = client.get("/api/entities/", params={"search": "CA"})
    assert len(resp.json()) == 1


def test_update_entity(client):
    resp = client.post("/api/entities/", json={
        "name": "Old Name", "jurisdiction": "DE", "entity_type": "corporation",
    })
    entity_id = resp.json()["id"]

    resp = client.put(f"/api/entities/{entity_id}", json={"name": "New Name"})
    assert resp.status_code == 200
    assert resp.json()["name"] == "New Name"


def test_delete_entity(client):
    resp = client.post("/api/entities/", json={
        "name": "Doomed Corp", "jurisdiction": "DE", "entity_type": "corporation",
    })
    entity_id = resp.json()["id"]

    resp = client.delete(f"/api/entities/{entity_id}")
    assert resp.status_code == 204

    resp = client.get(f"/api/entities/{entity_id}")
    assert resp.status_code == 404


def test_entity_not_found(client):
    resp = client.get("/api/entities/999")
    assert resp.status_code == 404
