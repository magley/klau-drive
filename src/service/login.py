import json

import requests
from src.service.session import BASE_URL


class NoSuchUserException(Exception):
    pass


def login(username: str, password: str):
    payload = {
        "username": username,
        "password": password,
    }
    payload_json = json.dumps(payload, default=str)

    r = requests.post(f'{BASE_URL}/login', data=payload_json)
    status_code = r.status_code
    body = r.json()

    if status_code == 200:
        return body["token"]
    elif status_code == 401:
        raise NoSuchUserException("No such user with that password: " + username)
    else:
        raise RuntimeError("Fatal error: " + str(body))
