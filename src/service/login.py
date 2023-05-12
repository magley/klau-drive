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
    body = json.loads(p['body'])

    if p['statusCode'] == 200:
        return body["token"]
    elif p['statusCode'] == 401:
        raise NoSuchUserException("No such user with that password: " + username)