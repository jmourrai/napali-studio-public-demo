"""FastAPI interface for local-only workflow demonstration."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator

from app.storage import ALLOWED, InvalidTransition, MissingItem, StaleVersion, Store

ROOT = Path(__file__).resolve().parents[1]


class NewItem(BaseModel):
    title: str = Field(min_length=3, max_length=100)
    description: str = Field(default="", max_length=500)
    priority: str = "medium"

    @field_validator("title")
    @classmethod
    def title_not_whitespace(cls, title: str) -> str:
        value = title.strip()
        if len(value) < 3:
            raise ValueError("Title must have at least three visible characters")
        return value

    @field_validator("priority")
    @classmethod
    def valid_priority(cls, priority: str) -> str:
        if priority not in {"low", "medium", "high"}:
            raise ValueError("Priority must be low, medium, or high")
        return priority


class ChangeStatus(BaseModel):
    to_status: str
    expected_version: int = Field(ge=1)
    note: str = Field(default="", max_length=250)


def create_app(db_path: str | None = None, seed: bool | None = None) -> FastAPI:
    path = db_path or os.environ.get("DEMO_DB_PATH", str(ROOT / ".data" / "workflows.sqlite"))
    use_seed = (os.environ.get("DEMO_SEED", "true").lower() == "true") if seed is None else seed
    store = Store(path)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        store.initialize()
        if use_seed:
            store.seed()
        yield

    app = FastAPI(
        title="Nā Pali Studio — Public Engineering Demo",
        description="Independent synthetic example, not the private Nā Pali Studio platform",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.mount("/static", StaticFiles(directory=ROOT / "web"), name="static")

    @app.get("/", include_in_schema=False)
    def index():
        return FileResponse(ROOT / "web" / "index.html")

    @app.get("/healthz")
    def healthz():
        return {"status": "ok"}

    @app.get("/readyz")
    def readyz():
        try:
            store.counts()
        except Exception as exc:
            raise HTTPException(status_code=503, detail="Database unavailable") from exc
        return {"status": "ready"}

    @app.get("/api/work-items")
    def list_items():
        return store.list_items()

    @app.post("/api/work-items", status_code=201)
    def create_item(item: NewItem):
        return store.create_item(**item.model_dump())

    @app.get("/api/work-items/{item_id}")
    def get_item(item_id: str):
        try:
            return store.get_item(item_id)
        except MissingItem as exc:
            raise HTTPException(404, "Work item not found") from exc

    @app.post("/api/work-items/{item_id}/transition")
    def change_status(item_id: str, payload: ChangeStatus):
        try:
            return store.transition(item_id, **payload.model_dump())
        except MissingItem as exc:
            raise HTTPException(404, "Work item not found") from exc
        except (InvalidTransition, StaleVersion) as exc:
            raise HTTPException(409, str(exc)) from exc

    @app.get("/api/work-items/{item_id}/events")
    def events(item_id: str):
        try:
            return store.audit(item_id)
        except MissingItem as exc:
            raise HTTPException(404, "Work item not found") from exc

    @app.get("/api/metrics")
    def metrics():
        return store.counts()

    @app.get("/api/workflow")
    def workflow():
        return {"allowed_transitions": {status: sorted(next_states)
                                        for status, next_states in ALLOWED.items()}}

    return app


app = create_app()
