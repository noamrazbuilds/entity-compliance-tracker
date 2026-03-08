from datetime import date, timedelta


def _create_entity(client, name="Test Corp"):
    resp = client.post("/api/entities/", json={
        "name": name, "jurisdiction": "DE", "entity_type": "corporation",
    })
    return resp.json()["id"]


def test_create_filing(client):
    entity_id = _create_entity(client)
    resp = client.post(f"/api/entities/{entity_id}/filings", json={
        "filing_type": "Annual Report",
        "jurisdiction": "DE",
        "due_date": str(date.today() + timedelta(days=30)),
    })
    assert resp.status_code == 201
    assert resp.json()["filing_type"] == "Annual Report"
    assert resp.json()["status"] == "pending"


def test_upcoming_filings(client):
    entity_id = _create_entity(client)
    # One upcoming, one far out
    client.post(f"/api/entities/{entity_id}/filings", json={
        "filing_type": "Annual Report",
        "jurisdiction": "DE",
        "due_date": str(date.today() + timedelta(days=15)),
    })
    client.post(f"/api/entities/{entity_id}/filings", json={
        "filing_type": "Franchise Tax",
        "jurisdiction": "DE",
        "due_date": str(date.today() + timedelta(days=120)),
    })

    resp = client.get("/api/filings/upcoming", params={"days": 30})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["filing_type"] == "Annual Report"


def test_overdue_filings(client):
    entity_id = _create_entity(client)
    client.post(f"/api/entities/{entity_id}/filings", json={
        "filing_type": "Annual Report",
        "jurisdiction": "DE",
        "due_date": str(date.today() - timedelta(days=5)),
        "status": "pending",
    })
    # Filed one should not appear
    client.post(f"/api/entities/{entity_id}/filings", json={
        "filing_type": "Franchise Tax",
        "jurisdiction": "DE",
        "due_date": str(date.today() - timedelta(days=10)),
        "status": "filed",
    })

    resp = client.get("/api/filings/overdue")
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_mark_as_filed(client):
    entity_id = _create_entity(client)
    resp = client.post(f"/api/entities/{entity_id}/filings", json={
        "filing_type": "Annual Report",
        "jurisdiction": "DE",
        "due_date": str(date.today() + timedelta(days=10)),
    })
    filing_id = resp.json()["id"]

    resp = client.post(f"/api/filings/{filing_id}/mark-filed")
    assert resp.status_code == 200
    assert resp.json()["status"] == "filed"
    assert resp.json()["filed_date"] is not None
