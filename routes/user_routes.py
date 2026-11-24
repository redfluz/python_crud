import re


ROUTES = (
    ("GET", re.compile(r"^/$"), "index"),
    ("GET", re.compile(r"^/users/new$"), "new"),
    ("POST", re.compile(r"^/users$"), "create"),
    ("GET", re.compile(r"^/users/([1-9][0-9]*)/edit$"), "edit"),
    ("POST", re.compile(r"^/users/([1-9][0-9]*)/update$"), "update"),
    ("POST", re.compile(r"^/users/([1-9][0-9]*)/delete$"), "delete"),
)


def resolve(method, path):
    for route_method, pattern, handler in ROUTES:
        if method != route_method:
            continue

        match = pattern.fullmatch(path)

        if match:
            return handler, match.groups()

    return None, ()