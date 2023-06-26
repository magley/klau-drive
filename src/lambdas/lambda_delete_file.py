from .common import *


def get_all_owners(username: str, uuid: str):
    album_uuids = []
    for album in get_albums(username):
        statement = f"""
            SELECT * FROM {TB_ALBUM_FILES_NAME}
            WHERE
                {TB_ALBUM_FILES_PK}=?
                    AND
                {TB_ALBUM_FILES_SK}=?
        """
        parameters = python_obj_to_dynamo_obj([album[TB_USER_ALBUMS_SK], uuid])

        response = dynamo_cli.execute_statement(  
            Statement=statement,
            Parameters=parameters
        )

        for o in response['Items']:
            obj = dynamo_obj_to_python_obj(o)
            album_uuids.append(obj[TB_ALBUM_FILES_PK])

    return list(set(album_uuids))


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
    if file_uuid in [o[TB_USER_ALBUMS_SK] for o in get_albums(username)]:
        remove_album(username, album_uuid, file_uuid) # Recursive
    else:
        remove_single_file(username, album_uuid, file_uuid)


def remove_single_file(username: str, album_uuid: str, file_uuid: str):
    key = {
        CONTENT_METADATA_TB_PK: username,
        CONTENT_METADATA_TB_SK: file_uuid
    }

    all_owners = get_all_owners(username, file_uuid)

    if len(all_owners) == 1: # If this file is only in 1 album.
        # Removing all sharing instances

        remove_sharing_instances(username, file_uuid)
        
        # Remove metadata.

        dynamo_cli.delete_item(
            Key=python_obj_to_dynamo_obj(key),
            TableName=CONTENT_METADATA_TB_NAME,
        )

        # Mark content for removal.

        dynamo_cli.put_item(
            TableName=TB_GARBAGE_COLLECTOR_NAME,
            Item=python_obj_to_dynamo_obj({
                TB_GARBAGE_COLLECTOR_PK: username,
                TB_GARBAGE_COLLECTOR_SK: file_uuid,
            })
        )

    # Remove from this album.

    dynamo_cli.delete_item(
        TableName=TB_ALBUM_FILES_NAME,
        Key=python_obj_to_dynamo_obj({
            TB_ALBUM_FILES_PK: album_uuid,
            TB_ALBUM_FILES_SK: file_uuid
        })
    )


def remove_album(username: str, owner_album_uuid: str, album_uuid: str):
    remove_sharing_instances(username, album_uuid)
    
    # Remove each subfile: THIS HAS TO GO BEFORE BECAUSE:
    # if you remove [user-album], then when you delete a single file:
    # it checks for all abums that have that file. The way it checks needs the
    # [user-album] relationship because it'll return one less item. If the file
    # has only 1 owner, it gets deleted for real. So the S3 item and metadata are
    # gone, but it may have one more owner. When you do list files on THAT other
    # owner, it won't be able to fetch metadata and your app will crash.

    items = get_album_files(album_uuid)
    for o in items:
        album_item = dynamo_obj_to_python_obj(o)
        item_uuid = album_item[TB_ALBUM_FILES_SK]
        delete(username, album_uuid, item_uuid)

    # Remove from user's list of albums.
  
    dynamo_cli.delete_item(
        TableName=TB_USER_ALBUMS_NAME,
        Key=python_obj_to_dynamo_obj({
            TB_USER_ALBUMS_PK: username,
            TB_USER_ALBUMS_SK: album_uuid,
        })
    )
    dynamo_cli.delete_item(
        TableName=TB_ALBUM_FILES_NAME,
        Key=python_obj_to_dynamo_obj({
            TB_ALBUM_FILES_PK: owner_album_uuid,
            TB_ALBUM_FILES_SK: album_uuid,
        })
    )



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