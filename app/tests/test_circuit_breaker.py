import pytest
import time
from app.utils.circuit_breaker import CircuitBreaker


def test_circuit_breaker_closes_on_success():
    cb = CircuitBreaker(failure_threshold=3, recovery_timeout=2)
    # fresh CB should allow
    assert cb.allow_request()
    # simulate success
    cb.record_success()
    assert cb.state == "CLOSED"


def test_circuit_breaker_opens_on_failures():
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout=2)
    cb.record_failure()
    cb.record_failure()
    assert cb.state == "OPEN"
    # should refuse request
    assert not cb.allow_request()


def test_circuit_breaker_half_open_and_recover():
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout=1)
    cb.record_failure()
    cb.record_failure()
    assert cb.state == "OPEN"
    time.sleep(1.5)  # allow recovery
    assert cb.allow_request()  # half-open
    # simulate a success in half-open
    cb.record_success()
    assert cb.state == "CLOSED"


def test_circuit_breaker_stays_closed_if_no_failures():
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout=2)
    for _ in range(5):
        cb.record_success()
    assert cb.state == "CLOSED"
    assert cb.allow_request()
