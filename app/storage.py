"""SQLite persistence and auditable state changes for an intentionally small demo.

This is new illustrative code. It does not reproduce the private product's data model.
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator
from uuid import uuid4

WORKFLOW = ("intake", "review", "in_progress", "approval", "published")
ALLOWED = {
    "intake": {"review"},
    "review": {"intake", "in_progress"},
    "in_progress": {"review", "approval"},
    "approval": {"in_progress", "published"},
    "published": set(),
}


class MissingItem(Exception):
    pass


class InvalidTransition(Exception):
    pass


class StaleVersion(Exception):
    pass


def timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Store:
    def __init__(self, db_path: str | Path):
        self.db_path = str(db_path)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.db_path, timeout=5, isolation_level=None)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA busy_timeout=5000")
        try:
            yield connection
        finally:
            connection.close()

    def initialize(self) -> None:
        with self.connect() as con:
            con.executescript(
                """
                PRAGMA journal_mode=WAL;
                CREATE TABLE IF NOT EXISTS work_items (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL DEFAULT '',
                    priority TEXT NOT NULL CHECK(priority IN ('low','medium','high')),
                    status TEXT NOT NULL CHECK(status IN
                        ('intake','review','in_progress','approval','published')),
                    version INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    work_item_id TEXT NOT NULL REFERENCES work_items(id),
                    from_status TEXT,
                    to_status TEXT NOT NULL,
                    note TEXT NOT NULL DEFAULT '',
                    actor TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_items_status ON work_items(status);
                CREATE INDEX IF NOT EXISTS idx_events_item ON events(work_item_id, id);
                """
            )

    def list_items(self) -> list[dict]:
        with self.connect() as con:
            return [dict(x) for x in con.execute(
                "SELECT * FROM work_items ORDER BY created_at, id"
            ).fetchall()]

    def get_item(self, item_id: str) -> dict:
        with self.connect() as con:
            row = con.execute("SELECT * FROM work_items WHERE id = ?", (item_id,)).fetchone()
            if row is None:
                raise MissingItem(item_id)
            return dict(row)

    def create_item(self, *, title: str, description: str = "", priority: str = "medium") -> dict:
        item_id = str(uuid4())
        now = timestamp()
        with self.connect() as con:
            con.execute("BEGIN IMMEDIATE")
            con.execute(
                """INSERT INTO work_items(id,title,description,priority,status,version,created_at,updated_at)
                VALUES (?,?,?,?, 'intake',1,?,?)""",
                (item_id, title, description, priority, now, now),
            )
            con.execute(
                """INSERT INTO events(work_item_id,from_status,to_status,note,actor,created_at)
                VALUES (?,NULL,'intake','Created in demo','demo-user',?)""",
                (item_id, now),
            )
            con.commit()
        return self.get_item(item_id)

    def transition(self, item_id: str, *, to_status: str, expected_version: int,
                   note: str = "") -> dict:
        if to_status not in WORKFLOW:
            raise InvalidTransition(f"Unknown workflow state: {to_status}")
        with self.connect() as con:
            con.execute("BEGIN IMMEDIATE")
            original = con.execute(
                "SELECT status,version FROM work_items WHERE id = ?", (item_id,)
            ).fetchone()
            if original is None:
                con.rollback()
                raise MissingItem(item_id)
            if original["version"] != expected_version:
                con.rollback()
                raise StaleVersion("Work item changed since you loaded it; refresh and retry")
            if to_status not in ALLOWED[original["status"]]:
                con.rollback()
                raise InvalidTransition(
                    f"Cannot move directly from {original['status']} to {to_status}"
                )
            now = timestamp()
            con.execute(
                """UPDATE work_items SET status = ?, version = version + 1, updated_at = ?
                WHERE id = ? AND version = ?""",
                (to_status, now, item_id, expected_version),
            )
            con.execute(
                """INSERT INTO events(work_item_id,from_status,to_status,note,actor,created_at)
                VALUES (?,?,?,?, 'demo-user',?)""",
                (item_id, original["status"], to_status, note, now),
            )
            con.commit()
        return self.get_item(item_id)

    def audit(self, item_id: str) -> list[dict]:
        self.get_item(item_id)
        with self.connect() as con:
            return [dict(x) for x in con.execute(
                """SELECT id,work_item_id,from_status,to_status,note,actor,created_at
                FROM events WHERE work_item_id=? ORDER BY id DESC""", (item_id,)
            ).fetchall()]

    def counts(self) -> dict:
        with self.connect() as con:
            rows = con.execute(
                "SELECT status,COUNT(*) AS count FROM work_items GROUP BY status"
            ).fetchall()
            totals = {status: 0 for status in WORKFLOW}
            totals.update({row["status"]: row["count"] for row in rows})
            return {"total": sum(totals.values()), "by_status": totals}

    def seed(self) -> None:
        if self.counts()["total"]:
            return
        for title, desc, priority, states in [
            ("Draft example release note", "Demonstrate a generic review workflow", "high", ["review"]),
            ("Validate sample dashboard", "Synthetic metrics and display checks", "medium", ["review", "in_progress"]),
            ("Approve placeholder summary", "Contains no real business or client information", "high", ["review", "in_progress", "approval"]),
            ("Publish demonstration guide", "Safe documentation using fabricated content", "low", ["review", "in_progress", "approval", "published"]),
            ("Triage new sample request", "Illustrative backlog item only", "medium", []),
        ]:
            item = self.create_item(title=title, description=desc, priority=priority)
            for state in states:
                item = self.transition(item["id"], to_status=state, expected_version=item["version"],
                                       note="Synthetic demonstration progression")
