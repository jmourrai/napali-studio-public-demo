from pathlib import Path

import pytest

from app.storage import InvalidTransition, MissingItem, StaleVersion, Store


@pytest.fixture
def store(tmp_path: Path):
    db = Store(tmp_path / "sample.sqlite")
    db.initialize()
    return db


def test_new_item_has_audit_event(store):
    item = store.create_item(title="Synthetic task", priority="high")
    assert item["status"] == "intake"
    assert item["version"] == 1
    audit = store.audit(item["id"])
    assert len(audit) == 1
    assert audit[0]["from_status"] is None


def test_transition_advances_version_and_tracks_audit(store):
    item = store.create_item(title="Synthetic task")
    changed = store.transition(item["id"], to_status="review", expected_version=1,
                               note="Ready for generic review")
    assert changed["version"] == 2
    assert changed["status"] == "review"
    assert store.audit(item["id"])[0]["note"] == "Ready for generic review"


def test_rejects_state_skipping(store):
    item = store.create_item(title="Synthetic task")
    with pytest.raises(InvalidTransition):
        store.transition(item["id"], to_status="published", expected_version=1)
    assert store.get_item(item["id"])["version"] == 1


def test_stale_update_does_not_change_data(store):
    item = store.create_item(title="Synthetic task")
    store.transition(item["id"], to_status="review", expected_version=1)
    with pytest.raises(StaleVersion):
        store.transition(item["id"], to_status="review", expected_version=1)
    assert len(store.audit(item["id"])) == 2


def test_missing_item(store):
    with pytest.raises(MissingItem):
        store.get_item("unknown")


def test_metrics_and_seed_are_idempotent(store):
    store.seed()
    assert store.counts()["total"] == 5
    store.seed()
    assert store.counts()["total"] == 5
    assert store.counts()["by_status"]["published"] == 1


def test_review_loop_is_explicit(store):
    item = store.create_item(title="Synthetic task")
    item = store.transition(item["id"], to_status="review", expected_version=1)
    item = store.transition(item["id"], to_status="intake", expected_version=2)
    assert item["status"] == "intake"
    assert len(store.audit(item["id"])) == 3


def test_published_is_terminal(store):
    store.seed()
    published = next(i for i in store.list_items() if i["status"] == "published")
    with pytest.raises(InvalidTransition):
        store.transition(published["id"], to_status="approval",
                         expected_version=published["version"])
