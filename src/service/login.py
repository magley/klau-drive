import json
from src.service.session import lambda_cli


class NoSuchUserException(Exception):
    pass

LAMBDA_NAME = "login"


def login(username: str, password: str):
    payload = {
        "body": {
            "username": username,
            "password": password,
        },
    }
    payload_json = json.dumps(payload, default=str)

    result = lambda_cli.invoke(
        FunctionName=LAMBDA_NAME,
        Payload=payload_json
    )

    p = json.loads(result['Payload'].read())
    body = p['body']

    if body is None:
        raise NoSuchUserException("No such user with that password: " + username)

    return body["token"]