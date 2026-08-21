from datetime import datetime, timedelta


def test_expenses_endpoints_crud(client):
    # create an expense
    payload = {
        "expense": "Test Coffee",
        "total": 2.75,
        "category": "beverages",
        "date": datetime.utcnow().isoformat()
    }

    post_resp = client.post("/expenses/", json=payload)
    assert post_resp.status_code == 201
    data = post_resp.json()
    assert "id" in data
    expense_id = data["id"]

    # the API accepts uppercase enum names and normalizes them to the database enum values
    uppercase_payload = {
        "expense": "Uppercase category", "total": 18.50, "category": "FOOD", "date": datetime.utcnow().isoformat()
    }
    uppercase_resp = client.post("/expenses/", json=uppercase_payload)
    assert uppercase_resp.status_code == 201
    assert uppercase_resp.json()["category"] == "food"

    # batch creation atomic call
    batch_payload = {
        "items": [
            {"expense": "Batch item 1", "total": 12.00, "category": "food", "date": datetime.utcnow().isoformat()},
            {"expense": "Batch item 2", "total": 7.50, "category": "operation", "date": datetime.utcnow().isoformat()}
        ]
    }
    batch_resp = client.post("/expenses/batch", json=batch_payload)
    assert batch_resp.status_code == 201
    batch_data = batch_resp.json()
    assert isinstance(batch_data, list)
    assert len(batch_data) == 2

    # get by id
    get_resp = client.get(f"/expenses/{expense_id}")
    assert get_resp.status_code == 200
    got = get_resp.json()
    assert got["id"] == expense_id
    assert got["expense"] == "Test Coffee"

    # list by date
    target_date = datetime.utcnow().date().isoformat()
    list_resp = client.get("/expenses/", params={"date": target_date})
    assert list_resp.status_code == 200
    list_data = list_resp.json()
    assert isinstance(list_data, list)
    assert any(item["id"] == expense_id for item in list_data)

    # range query
    start = (datetime.utcnow() - timedelta(days=1)).date().isoformat()
    end = (datetime.utcnow() + timedelta(days=1)).date().isoformat()
    rresp = client.get("/expenses/range", params={"start": start, "end": end})
    assert rresp.status_code == 200
    rdata = rresp.json()
    assert any(item["id"] == expense_id for item in rdata)

    # patch update
    patch_resp = client.patch(f"/expenses/{expense_id}", json={"total": 5.0})
    assert patch_resp.status_code == 200
    pdat = patch_resp.json()
    assert pdat["total"] == 5.0

    # delete
    del_resp = client.delete(f"/expenses/{expense_id}")
    assert del_resp.status_code == 204

    # confirm deleted - request JSON accept header so exception is returned as JSON not a redirect
    get_after = client.get(f"/expenses/{expense_id}", headers={"accept": "application/json"})
    assert get_after.status_code == 404
