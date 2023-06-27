import base64
import json
import boto3
from os import environ
from boto3.dynamodb.types import TypeSerializer, TypeDeserializer

NOTIFICATIONS_SENDER_EMAIL = "test@example.com"

GARBAGE_QUEUE_URL = environ["GARBAGE_QUEUE_URL"]

CONTENT_BUCKET_NAME = environ["CONTENT_BUCKET_NAME"]
CONTENT_METADATA_TB_NAME = environ["CONTENT_METADATA_TB_NAME"]
CONTENT_METADATA_TB_PK = "username"
CONTENT_METADATA_TB_SK = "uuid"

USER_TB_NAME = environ["USER_TB_NAME"]
USER_TB_PK = "username"

TB_USER_ALBUMS_NAME = "user_albums" # TODO: Use environ[...] like USER_TB_NAME.
TB_USER_ALBUMS_PK = "username"
TB_USER_ALBUMS_SK = "album_uuid"
TB_USER_ALBUMS_FIELD_NAME = "name"

TB_ALBUM_FILES_NAME = "album_files"
TB_ALBUM_FILES_PK = "album_uuid"
TB_ALBUM_FILES_SK = "uuid"

TB_ALBUM_FILES_FIELD_TYPE__FILE = "file"
TB_ALBUM_FILES_FIELD_TYPE__ALBUM = "album"
TB_ALBUM_FILES_FIELD_TYPE = "type" # TB_ALBUM_FILES_FIELD_TYPE__*

TB_FILE_IS_SHARED_NAME = "fileIsShared"
TB_FILE_IS_SHARED_PK = "uuid"
TB_FILE_IS_SHARED_SK = "username"

TB_SHARED_WITH_ME_NAME = "sharedWithMe"
TB_SHARED_WITH_ME_PK = "username"
TB_SHARED_WITH_ME_SK = "uuid"
TB_SHARED_WITH_ME_FIELD_TYPE = "type" # TB_ALBUM_FILES_FIELD_TYPE__*
TB_SHARED_WITH_ME_FIELD_OWNER = "owner"

TB_LAST_VALID_CONTENT_NAME = "lastValidContent"
TB_LAST_VALID_CONTENT_PK = "uuid"

TB_GARBAGE_COLLECTOR_NAME = "garbageCollector"
TB_GARBAGE_COLLECTOR_PK = "username"
TB_GARBAGE_COLLECTOR_SK = "uuid"

ACCESS_KEY = 'test'
SECRET_KEY = 'test'
REGION = 'us-east-1'

ENDPOINT = environ["ENDPOINT"]
if "ENDPOINT" not in environ:
    raise Exception("Please add ENDPOINT to env")

session = boto3.Session(aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
s3_cli = session.client('s3', endpoint_url=ENDPOINT)
dynamo_cli = session.client('dynamodb', endpoint_url=ENDPOINT)
ses_cli = session.client('ses', endpoint_url=ENDPOINT)
sqs_cli = session.client('sqs', endpoint_url=ENDPOINT)


def python_obj_to_dynamo_obj(python_obj):
    serializer = TypeSerializer()

    if type(python_obj) is dict:
        return {
            k: serializer.serialize(v)
            for k, v in python_obj.items()
        }
    elif type(python_obj) is list:
        return [
            serializer.serialize(o) for o in python_obj
        ]
    else:
        return serializer.serialize(python_obj)


def dynamo_obj_to_python_obj(dynamo_obj):
    deserializer = TypeDeserializer()
    return {
        k: deserializer.deserialize(v)
        for k, v in dynamo_obj.items()
    }


# https://stackoverflow.com/a/68409773
def base64url_decode(input):
    return base64.urlsafe_b64decode(input + '==')


def base64url_encode(input):
    stringAsBytes = input.encode('ascii')
    stringAsBase64 = base64.urlsafe_b64encode(stringAsBytes).decode('utf-8').replace('=', '')
    return stringAsBase64


def verify_user(token: str) -> None:
    pass


def http_response(body, status_code: int) -> dict:
    return {
        "body": json.dumps(body, default=str),
        "isBase64Encoded": False,
        "statusCode": status_code,
        "headers": {
            "content-type": "application/json"
        }
    }

def jwt_decode(headers: dict) -> str:
    auth_header: str = headers['Authorization']
    parts = auth_header.split()
    jwt = parts[1]

    jwt_body_str: str = jwt.split('.')[1]
    jwt_body: dict = json.loads(base64url_decode(jwt_body_str))
    username = jwt_body['username']

    return username


def owns_that_file(username: str, file_uuid: str) -> bool:
    key = {
        CONTENT_METADATA_TB_PK: username,
        CONTENT_METADATA_TB_SK: file_uuid
    }

    response = dynamo_cli.get_item(
        TableName=CONTENT_METADATA_TB_NAME,
        Key=python_obj_to_dynamo_obj(key)
    )

    if 'Item' not in response:
        return False
    return True


def user_exists(username: str) -> bool:
    key = {
        USER_TB_PK: username,
    }

    response = dynamo_cli.get_item(
        TableName=USER_TB_NAME,
        Key=python_obj_to_dynamo_obj(key)
    )

    if 'Item' not in response:
        return False
    return True


def get_email(username: str) -> str:
    key = {
        USER_TB_PK: username,
    }
    response = dynamo_cli.get_item(
        TableName=USER_TB_NAME,
        Key=python_obj_to_dynamo_obj(key)
    )
    if "Item" not in response:
        return ""
    print(response["Item"])
    return response["Item"]["email"]["S"]


def get_albums(username: str):
    statement = f"""
        SELECT * FROM {TB_USER_ALBUMS_NAME}
        WHERE
            {TB_USER_ALBUMS_PK}=?
    """
    parameters = python_obj_to_dynamo_obj([username])

    response = dynamo_cli.execute_statement(  
        Statement=statement,
        Parameters=parameters
    )

    albums = []
    for o in response['Items']:
        obj = dynamo_obj_to_python_obj(o)
        albums.append(obj)
    return albums


def get_album_files(album_uuid: str) -> list:
    """
        RETURNS A DYNAMO OBJECT
    """
    statement = f"""
        SELECT * FROM {TB_ALBUM_FILES_NAME}
        WHERE
            {TB_ALBUM_FILES_PK}=?
    """
    parameters = python_obj_to_dynamo_obj([album_uuid])

    response = dynamo_cli.execute_statement(    
        Statement=statement,
        Parameters=parameters
    )

    return response['Items']


def get_everything_shared(username: str) -> list:
    statement = f"""
        SELECT * FROM {TB_SHARED_WITH_ME_NAME}
        WHERE
            {TB_SHARED_WITH_ME_PK}=?
    """
    parameters = python_obj_to_dynamo_obj([username])

    response = dynamo_cli.execute_statement(  
        Statement=statement,
        Parameters=parameters
    )

    return response['Items']


def album_uuid_to_album_metadata(username: str, album_uuid: str) -> dict:
    statement = f"""
        SELECT * FROM {TB_USER_ALBUMS_NAME}
        WHERE
            {TB_USER_ALBUMS_PK}=? AND
            {TB_USER_ALBUMS_SK}=?
    """
    parameters = python_obj_to_dynamo_obj([username, album_uuid])

    response = dynamo_cli.execute_statement(    
        Statement=statement,
        Parameters=parameters
    )

    for o in response['Items']:
        obj = dynamo_obj_to_python_obj(o)
        return obj # There should be only 1.
    return {}


def file_uuid_to_file_metadata(username: str, file_uuid: str) -> dict:
    statement = f"""
        SELECT * FROM {CONTENT_METADATA_TB_NAME}
        WHERE
            {CONTENT_METADATA_TB_PK}=? AND
            {CONTENT_METADATA_TB_SK}=?
    """
    parameters = python_obj_to_dynamo_obj([username, file_uuid])

    response = dynamo_cli.execute_statement(    
        Statement=statement,
        Parameters=parameters
    )

    for o in response['Items']:
        obj = dynamo_obj_to_python_obj(o)
        return obj # There should be only 1.
    return {}   


def is_shared_directly(username: str, uuid: str):
    """
        FILES OR ALBUMS
    """
    statement = f"""
        SELECT * FROM {TB_SHARED_WITH_ME_NAME}
        WHERE
            {TB_SHARED_WITH_ME_PK}=?
                AND
            {TB_SHARED_WITH_ME_SK}=?
    """
    parameters = python_obj_to_dynamo_obj([username, uuid])

    response = dynamo_cli.execute_statement(  
        Statement=statement,
        Parameters=parameters
    )

    for o in response['Items']:
        return True
    return False


def is_file_owned_by_me(username: str, file_uuid: str):
    statement = f"""
        SELECT * FROM {CONTENT_METADATA_TB_NAME}
        WHERE
            {CONTENT_METADATA_TB_PK}=? AND
            {CONTENT_METADATA_TB_SK}=?
    """
    parameters = python_obj_to_dynamo_obj([username, file_uuid])

    response = dynamo_cli.execute_statement(    
        Statement=statement,
        Parameters=parameters
    )

    for o in response['Items']:
        return True
    return False


def is_album_owned_by_me(username: str, album_uuid: str):
    statement = f"""
        SELECT * FROM {TB_USER_ALBUMS_NAME}
        WHERE
            {TB_USER_ALBUMS_PK}=? AND
            {TB_USER_ALBUMS_SK}=?
    """
    parameters = python_obj_to_dynamo_obj([username, album_uuid])

    response = dynamo_cli.execute_statement(    
        Statement=statement,
        Parameters=parameters
    )

    for o in response['Items']:
        return True
    return False
    

def is_shared_with_me(target_uuid: str, username: str, owner: str):
    """
        Recursive. For direct sharing, see: `is_shared_directly`.
    """
    
    all_albums = get_albums(owner)
    for album in all_albums:
        album_content = [dynamo_obj_to_python_obj(o) for o in get_album_files(album[TB_USER_ALBUMS_SK])]
        album['content'] = album_content

    reverse_lookup = {}
    for album in all_albums:
        for item in album['content']:
            if item['uuid'] not in item:
                reverse_lookup[item['uuid']] = []

            reverse_lookup[item['uuid']].append(item['album_uuid'])
    """
        all_albums = [
            {
                "uuid": album_uuid,
                "content": [
                    "uuid": uuid,
                    "album_uuid": album_uuid,
                    "type": file/folder
                ]
            }
        ]

        reverse_lookup = {
            uuid1: uuid_of_owner_of_uuid1,
            uuid2: ...
        }
    """

    queue = [target_uuid]
    while len(queue) > 0:
        current_uuid = queue[0]
        queue = queue[1:]

        if is_shared_directly(username, current_uuid):
            return True
        
        if current_uuid not in reverse_lookup:
            continue

        owners_uuid = reverse_lookup[current_uuid]
        for o in owners_uuid:
            queue.append(o)

    return False


def has_write_accesss(username: str, uuid: str):
    if is_file_owned_by_me(username, uuid):
        return True
    return is_album_owned_by_me(username, uuid)


def has_read_access(username: str, uuid: str, owner: str):
    if has_write_accesss(username, uuid):
        return True
    return is_shared_with_me(uuid, username, owner)


def send_email(username: str, message: str, subject: str):
    try:
        email = get_email(username)
        if not email:
            return False
        ses_cli.send_email(Source=NOTIFICATIONS_SENDER_EMAIL, Destination={"ToAddresses": [email]},
                           Message={
                               "Subject": {"Data": subject, "Charset": "utf-8"},
                               "Body": {"Text": {"Data": message, "Charset": "utf-8"}}
                           })
    except Exception as e:
        return False
    return True
