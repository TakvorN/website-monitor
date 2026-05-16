import json
import sys

import pytest

from website_monitor.main import main


def test_main_no_urls_exits_with_code_2(monkeypatch, capsys):
    # Replace real CLI args with simulated terminal input.
    monkeypatch.setattr(sys, "argv", ["main.py"])

    with pytest.raises(SystemExit) as exc:
        main()

    captured = capsys.readouterr()

    assert exc.value.code == 2
    assert "No URLs provided" in captured.out


def test_main_success_exit_code_zero(monkeypatch):
    def fake_check_url(*args, **kwargs):
        return {
            "url": "https://example.com",
            "label": "OK",
            "status_code": 200,
            "duration_ms": 123.45,
        }

    monkeypatch.setattr(
        "website_monitor.main.check_url",
        fake_check_url,
    )
    monkeypatch.setattr(sys, "argv", ["main.py", "example.com"])

    with pytest.raises(SystemExit) as exc:
        main()

    assert exc.value.code == 0


def test_main_multiple_urls(monkeypatch, capsys):
    results = [
        {
            "url": "https://example.com",
            "label": "OK",
            "status_code": 200,
            "duration_ms": 100,
        },
        {
            "url": "https://google.com",
            "label": "CLIENT_ERROR",
            "status_code": 404,
            "duration_ms": 150,
        },
    ]

    def fake_check_url(*args, **kwargs):
        return results.pop(0)

    monkeypatch.setattr(
        "website_monitor.main.check_url",
        fake_check_url,
    )

    monkeypatch.setattr(
        sys,
        "argv",
        ["main.py", "example.com", "google.com"],
    )

    with pytest.raises(SystemExit) as exc:
        main()

    captured = capsys.readouterr()

    assert exc.value.code == 1
    assert "OK: 1" in captured.out
    assert "CLIENT_ERROR: 1" in captured.out
    assert "TOTAL: 2" in captured.out


def test_main_json_output(monkeypatch, capsys):
    def fake_check_url(*args, **kwargs):
        return {
            "url": "https://example.com",
            "label": "OK",
            "status_code": 200,
            "duration_ms": 123.45,
        }

    monkeypatch.setattr(
        "website_monitor.main.check_url",
        fake_check_url,
    )
    monkeypatch.setattr(
        sys,
        "argv",
        ["main.py", "example.com", "--json"],
    )

    with pytest.raises(SystemExit) as exc:
        main()

    captured = capsys.readouterr()
    data = json.loads(captured.out)

    assert exc.value.code == 0
    assert isinstance(data, list)
    assert data[0]["label"] == "OK"
    assert "Summary:" not in captured.out


def test_main_reads_urls_from_file(monkeypatch, tmp_path):
    def fake_check_url(*args, **kwargs):
        return {
            "url": "https://example.com",
            "label": "OK",
            "status_code": 200,
            "duration_ms": 123.45,
        }

    input_file = tmp_path / "urls.txt"
    input_file.write_text(
        """
# this is a comment
example.com

"""
    )

    monkeypatch.setattr(
        "website_monitor.main.check_url",
        fake_check_url,
    )

    monkeypatch.setattr(
        sys,
        "argv",
        ["main.py", "--file", str(input_file)],
    )

    with pytest.raises(SystemExit) as exc:
        main()

    assert exc.value.code == 0


def test_main_quiet_mode_outputs_only_label(monkeypatch, capsys):
    def fake_check_url(*args, **kwargs):
        return {
            "url": "https://example.com",
            "label": "OK",
            "status_code": 200,
            "duration_ms": 123.45,
        }

    monkeypatch.setattr(
        "website_monitor.main.check_url",
        fake_check_url,
    )
    monkeypatch.setattr(
        sys,
        "argv",
        ["main.py", "example.com", "--quiet"],
    )

    with pytest.raises(SystemExit) as exc:
        main()

    captured = capsys.readouterr()

    assert exc.value.code == 0
    assert captured.out.strip() == "OK"
    assert "https://example.com" not in captured.out
    assert "Summary:" not in captured.out


def test_main_fail_fast_stops_after_first_failure(monkeypatch):
    call_count = 0

    def fake_check_url(*args, **kwargs):
        nonlocal call_count
        call_count += 1

        return {
            "url": "https://example.com",
            "label": "TIMEOUT",
            "status_code": None,
            "duration_ms": 100.0,
        }

    monkeypatch.setattr(
        "website_monitor.main.check_url",
        fake_check_url,
    )
    monkeypatch.setattr(
        sys,
        "argv",
        ["main.py", "bad.com", "good.com", "--fail-fast"],
    )

    with pytest.raises(SystemExit) as exc:
        main()

    assert exc.value.code == 1
    assert call_count == 1


def test_main_uses_threadpool_when_workers_gt_one(monkeypatch):
    called = False

    class FakeExecutor:
        def __init__(self, max_workers):
            nonlocal called
            called = True

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def submit(self, fn, *args, **kwargs):
            class FakeFuture:
                def result(self):
                    return {
                        "url": "https://example.com",
                        "label": "OK",
                        "status_code": 200,
                        "duration_ms": 123.45,
                    }

            return FakeFuture()

    monkeypatch.setattr(
        "website_monitor.main.ThreadPoolExecutor",
        FakeExecutor,
    )
    monkeypatch.setattr(
        "website_monitor.main.as_completed",
        lambda futures: futures,
    )
    monkeypatch.setattr(
        sys,
        "argv",
        ["main.py", "example.com", "--workers", "2"],
    )

    with pytest.raises(SystemExit) as exc:
        main()

    assert exc.value.code == 0
    assert called is True