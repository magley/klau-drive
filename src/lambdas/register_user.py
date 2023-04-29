from dataclasses import dataclass, asdict
from dynamodb_json import json_util
from src.lambdas.session import dynamo_cli
from botocore.exceptions import ClientError
from src.lambdas.util import create_table_if_not_exists
from datetime import datetime


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


def register_user(user: User) -> str | None:
    create_table_if_not_exists(TB_USER_NAME, TB_USER_PK, None)

    user_ddb = json_util.dumps(asdict(user), as_dict=True)
    try:
        dynamo_cli.put_item(
            TableName=TB_USER_NAME,
            Item=user_ddb,
            ConditionExpression='attribute_not_exists(username)'
        )
        return None
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return 'Username already taken'
        else:
            raise e


def list_users():
    for user in dynamo_cli.scan(TableName=TB_USER_NAME)['Items']:
        print(user)
