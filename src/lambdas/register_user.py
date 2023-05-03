from dataclasses import dataclass, asdict
import json
from typing import Dict
from dynamodb_json import json_util
from src.lambdas.session import dynamo_cli
from botocore.exceptions import ClientError
from src.lambdas.util import create_table_if_not_exists
from datetime import datetime
from src.lambdas.session import lambda_cli


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

    return {
        "body": {
            "user": {
                **user_dict
            }
        }
    }
   

def register_user(user: User) -> str | None:
    payload = make_payload_from(user)
    payload_json = json.dumps(payload, default=str)

    result = lambda_cli.invoke(
        FunctionName=LAMBDA_NAME,
        Payload=payload_json
    )

    p = json.loads(result['Payload'].read())
    body = p['body']
    status = body['status']

    if status == 400:
        return 'Username already taken'
    
    return None


def list_users():
    for user in dynamo_cli.scan(TableName=TB_USER_NAME)['Items']:
        print(user)
