from .common import *
import io


def get_file(username: str, file_uuid: str):
    # TODO: Sharing: check if file is part of shared album hierarchy or if
    # the file is directly shared.

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
    return None


def download_file(file_uuid: str) -> str:
    stream = io.BytesIO()
    s3_cli.download_fileobj(
        Bucket=CONTENT_BUCKET_NAME,
        Key=file_uuid,
        Fileobj=stream
    )
    stream.seek(0)

    bytes_str = base64.b64encode(stream.getvalue()).decode()
    return bytes_str


def lambda_download_file(event: dict, context):
    body: dict = json.loads(event['body'])
    headers: dict = event['headers']

    username: str = jwt_decode(headers)
    if not user_exists(username):
        return http_response("Forbidden", 401)
 
    file_uuid = body['file_uuid']
    bucket_uri = f'{CONTENT_BUCKET_NAME}/{file_uuid}'
    bucket_key = file_uuid
    file = get_file(username, file_uuid)

    if file is None:
        return http_response("File not found", 404)

    bytes_str = download_file(file_uuid)
    return http_response(bytes_str, 200)