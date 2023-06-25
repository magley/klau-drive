from .common import *


def get_sharing_instances(uuid: str):
    statement = f"""
        SELECT * FROM {TB_FILE_IS_SHARED_NAME}
        WHERE
            {TB_FILE_IS_SHARED_PK}=?
    """
    parameters = python_obj_to_dynamo_obj([uuid])

    response = dynamo_cli.execute_statement(  
        Statement=statement,
        Parameters=parameters
    )

    shares = []
    for o in response['Items']:
        obj = dynamo_obj_to_python_obj(o)
        shares.append(obj)
    return shares

def remove_sharing_instances(owner: str, uuid: str):

    # Remove all sharing

    sharing_instances = get_sharing_instances(uuid)

    for o in sharing_instances:
        shared_with: str = o[TB_FILE_IS_SHARED_SK]

        statement1 = f"""
            DELETE FROM {TB_SHARED_WITH_ME_NAME}
            WHERE
                {TB_SHARED_WITH_ME_PK} = ?
                    AND
                {TB_SHARED_WITH_ME_SK} = ?
        """
        parameters1 = python_obj_to_dynamo_obj([shared_with, uuid])
        dynamo_cli.execute_statement(  
            Statement=statement1,
            Parameters=parameters1
        )


def delete(username: str, album_uuid: str, file_uuid: str):
    # Instead of checking if it's a file or album, we do it the lazy way and
    # delete both. If the key does not exist, aws won't crash.

    remove_single_file(username, album_uuid, file_uuid)
    remove_album(username, file_uuid) # Recursive


def remove_single_file(username: str, album_uuid: str, file_uuid: str):
    key = {
        CONTENT_METADATA_TB_PK: username,
        CONTENT_METADATA_TB_SK: file_uuid
    }
    remove_sharing_instances(username, file_uuid)

    # Remove metadata.

    dynamo_cli.delete_item(
        Key=python_obj_to_dynamo_obj(key),
        TableName=CONTENT_METADATA_TB_NAME,
    )

    # Remove from album.

    dynamo_cli.delete_item(
        TableName=TB_ALBUM_FILES_NAME,
        Key=python_obj_to_dynamo_obj({
            TB_ALBUM_FILES_PK: album_uuid,
            TB_ALBUM_FILES_SK: file_uuid
        })
    )

    # Remove content.

    s3_cli.delete_object(
        Bucket=CONTENT_BUCKET_NAME,
        Key=key[CONTENT_METADATA_TB_SK]
    )


def remove_album(username: str, album_uuid: str):
    remove_sharing_instances(username, album_uuid)
    
    # Remove from user's list of albums.

    dynamo_cli.delete_item(
        TableName=TB_USER_ALBUMS_NAME,
        Key=python_obj_to_dynamo_obj({
            TB_USER_ALBUMS_PK: username,
            TB_USER_ALBUMS_SK: album_uuid,
        })
    )

    # Remove each subfile 

    items = get_album_files(album_uuid)
    for o in items:
        album_item = dynamo_obj_to_python_obj(o)
        item_uuid = album_item[TB_ALBUM_FILES_SK]
        delete(username, album_uuid, item_uuid)


def lambda_delete_file(event: dict, context):
    body: dict = json.loads(event['body'])
    headers: dict = event['headers']

    username: str = jwt_decode(headers)
    if not user_exists(username):
        return http_response("Forbidden", 401)

    
    album_uuid: dict = body['album_uuid']
    file_uuid: str = body['uuid']

    if '_root' in file_uuid: # If it's a root folder
        return http_response("Cannot delete root album!", 400)

    if not has_write_accesss(username, file_uuid):
        return http_response("You don't own this.", 404)

    delete(username, album_uuid, file_uuid)

    return http_response(None, 204)