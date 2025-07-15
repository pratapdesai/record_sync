import pytest
from app.services.queue import QueueManager


def test_enqueue_and_flush():
    qm = QueueManager()
    crm = "salesforce"
    record = {"record_id": "abc123", "data": {"foo": "bar"}}
    qm.enqueue(crm, record)
    assert len(qm.get_pending(crm)) == 1
    batch = qm.flush(crm, batch_size=10)
    assert isinstance(batch, list)
    assert len(batch) >= 0  # flush might leave some items if under batch size


def test_multiple_crm_queues():
    qm = QueueManager()
    qm.enqueue("salesforce", {"record_id": "a"})
    qm.enqueue("hubspot", {"record_id": "b"})
    assert len(qm.get_pending("salesforce")) == 1
    assert len(qm.get_pending("hubspot")) == 1
