import socket
import re
import sys
from retry import retry, fibonacci, const

methods = ['OPTIONS', 'GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'TRACE',
           'CONNECT']
r_moved = re.compile("30[12] Moved")
r_location = re.compile("Location: .+//(.+)/\r\n")
r_host = re.compile(r"Host: (.+)\r\n")


def get_method():
    s = "Enter one of possible methods (OPTIONS, GET(default), HEAD, POST, " \
        "PUT, DELETE, TRACE, CONNECT): "
    method = input(s).upper()
    if method == "":
        return "GET"
    if method not in methods:
        get_method()
    return method


def get_target_request():
    target_req = input("Enter target request or Enter(default: /): ")
    return "/" if target_req == "" else target_req


def add_cookie():
    cookie = []
    while True:
        key_value = input("Enter 'key=value' or Enter to exit: ")
        if key_value == "":
            break
        cookie += key_value
    return 'Cookie: ' + '; '.join(cookie) + "\r\n"


def add_headers_to_request(request):
    while True:
        header = input(
            "Enter header(Header: value) or Cookie(to add Cookie) "
            "or Enter(to skip adding headers): ")
        if header == "":
            break
        if header == "Cookie":
            request += add_cookie()
        else:
            request += header + "\r\n"
    request += "\r\n"
    return request


def write_server_response_in_file(filename, data):
    with open(filename, "w") as file:
        print(data, file=file)


def handle_server_response(response):
    try:
        return response.decode('utf-8')
    except Exception as e:
        print(e)
        sys.exit(1)


def is_moved(data):
    if r_moved.search(data):
        return True
    return False


def parse_actual_location(data):
    return r_location.findall(data)[0]


def get_timeout_seconds():
    t = input("Enter timeout in seconds or Enter(default: 10 sec): ")
    return 10 if t == "" else float(t)


def get_filename():
    if input("Write server response in file? (Y/n): ") == 'Y':
        f = input("Filename or Enter(default: file.txt in project): ")
        return "file.txt" if f == "" else f
    else:
        return ""


def create_request(method, target_request, host):
    req = "{} {} HTTP/1.1\r\nHost: {}\r\n".format(method, target_request, host)
    req = add_headers_to_request(req)
    return req


@retry(interval=fibonacci(), max_tries=5)
def get_response_from_server(host, timeout, req):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        port = 80
        s.settimeout(timeout)
        s.connect((host, port))
        s.sendall(bytearray(req.encode()))
        data = s.recv(65536)
        return handle_server_response(data)


def update_request(req, loc):
    old_loc = r_host.findall(req)[0]
    req = req.replace(old_loc, loc, 1)
    return req


def redirect(data, timeout, req):
    loc = parse_actual_location(data)
    upd_req = update_request(req, loc)
    return get_response_from_server(loc, timeout, upd_req)


@retry(interval=const(1), max_tries=3,
       message="Incorrect input. Please, try again")
def get_hostname():
    host = input("Enter address or Enter (Default: www.ya.ru): ")
    host = "ya.ru" if host == "" else host
    socket.getaddrinfo(host, port=80)
    return host


def http_client():
    host = get_hostname()
    method = get_method()
    timeout = get_timeout_seconds()
    target_request = get_target_request()
    req = create_request(method, target_request, host)
    filename = get_filename()
    data = get_response_from_server(host, timeout, req)
    if filename != "":
        write_server_response_in_file(filename, data)
    if is_moved(data):
        print("Redirect")
        data = redirect(data, timeout, req)
    print(data)


if __name__ == '__main__':
    http_client()
