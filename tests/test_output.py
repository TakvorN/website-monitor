from output import print_result


def test_print_result_quiet(capsys):
    result = {
        "url": "https://example.com",
        "label": "OK",
        "status_code": 200,
        "duration_ms": 123.45,
    }

    print_result(result, quiet=True)

    captured = capsys.readouterr()

    assert captured.out.strip() == "OK"


def test_print_result_normal_output(capsys):
    result = {
        "url": "https://example.com",
        "label": "OK",
        "status_code": 200,
        "duration_ms": 123.45,
    }

    print_result(result)

    captured = capsys.readouterr()

    assert "https://example.com" in captured.out
    assert "OK" in captured.out
    assert "200" in captured.out
    assert "123.45" in captured.out



def test_print_result_without_status_code(capsys):
    result = {
        "url": "https://example.com",
        "label": "TIMEOUT",
        "status_code": None,
        "duration_ms": 123.45,
    }

    print_result(result)

    captured = capsys.readouterr()

    assert "TIMEOUT" in captured.out
    assert "123.45" in captured.out
    assert "None" not in captured.out