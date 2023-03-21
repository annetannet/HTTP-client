import pytest
from http import *
from retry import *


def mock_input(mocker, return_value):
    mocker.patch("builtins.input", return_value=return_value)


@pytest.mark.parametrize("user_input, expected_result", [
    ('POST', 'POST'),
    ('post', 'POST'),
    ('', 'GET'),
    ('get', 'GET'),
])
def test_get_method_correct_input(mocker, user_input, expected_result):
    mock_input(mocker, user_input)
    assert get_method() == expected_result


@pytest.mark.parametrize("incorrect_input", ['got', 'dcdchbwdkcb', 'пост'])
def test_get_method_incorrect_input(mocker, incorrect_input):
    mock_input(mocker, incorrect_input)
    with pytest.raises(RecursionError):
        get_method()


def test_get_target_request(mocker):
    mock_input(mocker, "")
    assert get_target_request() == "/"


@pytest.mark.parametrize("time_seconds, float_time", [
    ("0.1", 0.1),
    ("10", 10),
    ("", 10)
])
def test_get_timeout(mocker, time_seconds, float_time):
    mock_input(mocker, time_seconds)
    assert get_timeout_seconds() == float_time


def test_get_filename(mocker):
    mock_input(mocker, "")
    assert get_filename() == ""


@pytest.mark.parametrize("host, res", [
    ("google.com", "google.com"),
    ("", "ya.ru")
])
def test_get_hostname(mocker, host, res):
    mock_input(mocker, host)
    assert get_hostname() == res


def test_get_incorrect_hostname(mocker):
    mock_input(mocker, "gaevkSEN;s")
    mocker.patch("builtins.print")
    with pytest.raises(SystemExit):
        get_hostname()


def test_add_cookie(mocker):
    mock_input(mocker, '')
    assert add_cookie() == 'Cookie: \r\n'


def test_add_headers_to_request(mocker):
    mock_input(mocker, "")
    exp = "GET / HTTP/1.1\r\nHost: www.google.com\r\n\r\n"
    actual = add_headers_to_request(
        "GET / HTTP/1.1\r\nHost: www.google.com\r\n")
    assert actual == exp


def test_write_server_response_in_file():
    write_server_response_in_file("file.txt", "data")
    with open("file.txt") as file:
        assert file.read() == "data\n"


def test_handle_server_response_utf8():
    assert "decoded" == handle_server_response("decoded".encode("utf-8"))


@pytest.mark.parametrize("generator, correct_sequence", [
    (const(0), [0, 0, 0]),
    (const(1), [1, 1, 1, 1, 1]),
    (fibonacci(), [1, 1, 2, 3, 5, 8, 13])
])
def test_retry_generator(generator, correct_sequence):
    for number in correct_sequence:
        assert next(generator) == number


def test_is_moved():
    assert is_moved("301 Moved")


def test_is_not_moved():
    assert not is_moved("200 OK")


def test_parse_actual_location():
    assert "ya.ru" == parse_actual_location("Location: https://ya.ru/\r\n")


def test_update_location():
    assert "GET / HTTP/1.1\r\nHost: www.google.com\r\n\r\n" == update_request(
        "GET / HTTP/1.1\r\nHost: google.com\r\n\r\n", "www.google.com")


def test_create_request(mocker):
    expected = "GET / HTTP/1.1\r\nHost: ya.ru\r\nConnection: close\r\n\r\n"
    mocker.patch("main.add_headers_to_request", return_value=expected)
    assert expected == create_request("GET", "/", "ya.ru")


def test_get_response_from_server():
    resp = get_response_from_server(
        "google.com", 10, "GET / HTTP/1.1\r\nHost: google.com\r\n\r\n")[:12]
    assert "HTTP/1.1 301" == resp


def test_handle_server_response_fail(mocker):
    mocker.patch("builtins.print")
    with pytest.raises(SystemExit):
        handle_server_response("проверка".encode("cp1251"))


def test_get_response_from_server_fail(mocker):
    mocker.patch("builtins.print")
    req = "GET / HTTP/1.1\r\nHost: www.google.com\r\n\r\n"
    with pytest.raises(SystemExit):
        get_response_from_server("www.google.com", 10, req)


def test_redirect():
    data = "Location: https://ya.ru/\r\n"
    req = "GET / HTTP/1.1\r\nHost: ya.ru\r\nConnection: close\r\n\r\n"
    assert "HTTP/1.1 301 Moved permanently" == redirect(data, 10, req)[:30]


def test_retry(mocker):
    result = []
    mocker.patch("builtins.print", result.append)

    @retry()
    def func_return_value():
        return True

    assert func_return_value()
    assert result == []


@pytest.mark.parametrize("max_tries, expected", [
    (1, ["give up"]),
    (2, ["Retry..", "give up"]),
    (3, ["Retry..", "Retry..", "give up"])
])
def test_retry_on_exception(mocker, max_tries, expected):
    result = []
    mocker.patch("builtins.print", result.append)

    @retry(max_tries=max_tries, giveup=lambda ex: result.append("give up"))
    def func_raising_ex():
        raise Exception

    func_raising_ex()
    assert result == expected


if __name__ == '__main__':
    pytest.main()
