from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session
from fastapi.testclient import TestClient

from src.main import app
from src.database import get_db, get_session

# prepare in-memory engine and create tables
engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
SQLModel.metadata.create_all(engine)

# override dependency
def get_session_override():
    with Session(engine) as s:
        yield s

app.dependency_overrides[get_db] = get_session_override
app.dependency_overrides[get_session] = get_session_override

with TestClient(app) as client:
    payload = {
        "expense": "Debug Coffee",
        "total": 2.75,
        "category": "beverages",
        "date": datetime.utcnow().isoformat()
    }
    print("POST /expenses/ ->")
    r = client.post("/expenses/", json=payload)
    print(r.status_code, r.text)

    if r.status_code == 201:
        data = r.json()
        eid = data['id']
        print("GET /expenses/{eid}")
        g = client.get(f"/expenses/{eid}")
        print(g.status_code, g.text)

        target_date = datetime.utcnow().date().isoformat()
        print("GET /expenses/ date=", target_date)
        l = client.get("/expenses/", params={"date": target_date})
        print(l.status_code, l.text)

        start = (datetime.utcnow() - timedelta(days=1)).date().isoformat()
        end = (datetime.utcnow() + timedelta(days=1)).date().isoformat()
        print("GET /expenses/range start/end=", start, end)
        r = client.get("/expenses/range", params={"start": start, "end": end})
        print(r.status_code, r.text)

    else:
        print("Create failed - aborting debug run")
