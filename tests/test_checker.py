import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from checker import check_url


class MockResponse:
    def __init__(self, status_code):
        self.status_code = status_code


class MockSession:
    def __init__(self, status_code):
        self.status_code = status_code

    def get(self, *args, **kwargs):
        return MockResponse(self.status_code)



class SequenceSession:
    def __init__(self, responses):
        self.responses = responses  # list of responses/exceptions
        self.call_count = 0

    def get(self, *args, **kwargs):
        if self.call_count >= len(self.responses):
            raise Exception("No more responses configured")

        response = self.responses[self.call_count]
        self.call_count += 1

        if isinstance(response, Exception):
            raise response

        return MockResponse(response)
    


def test_check_url_ok():
    session = MockSession(200)

    result = check_url(
        session,
        "https://example.com",
        timeout=5,
        retries=1,
        slow_threshold=None,
        follow_redirects=False,
        json_output=False,
        quiet=True,
        user_agent="test"
    )

    assert result["label"] == "OK"
    assert result["status_code"] == 200


def test_check_url_redirect():
    session = MockSession(301)

    result = check_url(session, "https://example.com", 5, 1, None, False, False, True, "test")

    assert result["label"] == "REDIRECT"


def test_check_url_client_error():
    session = MockSession(404)

    result = check_url(session, "https://example.com", 5, 1, None, False, False, True, "test")

    assert result["label"] == "CLIENT_ERROR"


def test_check_url_server_error():
    session = MockSession(500)

    result = check_url(session, "https://example.com", 5, 1, None, False, False, True, "test")

    assert result["label"] == "SERVER_ERROR"


import requests

def test_check_url_timeout():
    class TimeoutSession:
        def get(self, *args, **kwargs):
            raise requests.exceptions.Timeout()

    result = check_url(
        TimeoutSession(),
        "https://example.com",
        5, 1, None, False, False, True, "test"
    )

    assert result["label"] == "TIMEOUT"
    assert result["status_code"] is None



import requests

def test_check_url_retries_then_success():
    session = SequenceSession([
        requests.exceptions.Timeout(),
        requests.exceptions.Timeout(),
        200
    ])

    result = check_url(
        session,
        "https://example.com",
        timeout=5,
        retries=3,
        slow_threshold=None,
        follow_redirects=False,
        json_output=False,
        quiet=True,
        user_agent="test"
    )

    assert result["label"] == "OK"
    assert session.call_count == 3


def test_check_url_all_retries_fail():
    session = SequenceSession([
        requests.exceptions.Timeout(),
        requests.exceptions.Timeout(),
        requests.exceptions.Timeout()
    ])

    result = check_url(
        session,
        "https://example.com",
        timeout=5,
        retries=3,
        slow_threshold=None,
        follow_redirects=False,
        json_output=False,
        quiet=True,
        user_agent="test"
    )

    assert result["label"] == "TIMEOUT"
    assert result["status_code"] is None
    assert session.call_count == 3


def test_check_url_retry_once_then_success():
    session = SequenceSession([
        requests.exceptions.ConnectionError(),
        200
    ])

    result = check_url(
        session,
        "https://example.com",
        5, 2, None, False, False, True, "test"
    )

    assert result["label"] == "OK"
    assert session.call_count == 2



def test_check_url_slow_response(monkeypatch):
    times = [1.0, 3.5]

    def fake_perf_counter():
        return times.pop(0)

    monkeypatch.setattr("checker.time.perf_counter", fake_perf_counter)

    session = MockSession(200)

    result = check_url(
        session,
        "https://example.com",
        timeout=5,
        retries=1,
        slow_threshold=1000,
        follow_redirects=False,
        json_output=False,
        quiet=True,
        user_agent="test"
    )

    assert result["label"] == "SLOW"