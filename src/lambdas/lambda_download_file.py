from .common import *
import io


def can_download_file(username: str, file_uuid: str, owner: str):
    if is_file_owned_by_me(username, file_uuid):
        return True
    
    return is_shared_with_me(file_uuid, username, owner)


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
    owner_name = body['owner']

    if not has_read_access(username, file_uuid, owner_name):
        return http_response("File not found.", 404)

    bytes_str = download_file(file_uuid)
    return http_response(bytes_str, 200)