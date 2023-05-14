from dataclasses import dataclass
import json
from typing import Dict

import requests
from src.service.session import BASE_URL, dynamo_cli
from datetime import datetime
from src.service.session import lambda_cli


@dataclass
class User:
    name: str | None
    surname: str | None
    # date_of_birth is datetime instead of date because json_util's
    # serializer knows how to serialize datetimes, but not dates.
    date_of_birth: datetime | None
    username: str
    email: str | None
    password: str


TB_USER_NAME = 'user'
TB_USER_PK = 'username'
LAMBDA_NAME = "register"


def make_payload_from(user: User) -> Dict:
    user_dict = vars(user) # Be careful if you ever add anything fancy to `User`

    return user_dict
   

def register_user(user: User) -> str | None:
    payload = make_payload_from(user)
    payload_json = json.dumps(payload, default=str)

    r = requests.post(f'{BASE_URL}/session', data=payload_json)
    status = r.status_code

    if status == 400:
        body = r.json()
        return body['message']
    
    return None


def list_users():
    for user in dynamo_cli.scan(TableName=TB_USER_NAME)['Items']:
        print(user)
