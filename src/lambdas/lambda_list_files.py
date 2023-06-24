
from .common import * 


def lambda_list_files(event: dict, context):
    body: dict = json.loads(event['body'])
    headers: dict = event['headers']
    album_uuid: str = body['album_uuid']
    album_owner: str = body['album_owner']

    username: str = jwt_decode(headers)
    if not user_exists(username):
        return http_response("Forbidden", 401)
    
    items = get_album_files(album_uuid)

    items_shared = []
    if 'root' in album_uuid:
        items_shared = get_everything_shared(username)

    result = []

    for o in items:
        album_item = dynamo_obj_to_python_obj(o)
        item_uuid = album_item[TB_ALBUM_FILES_SK]
        item_type = album_item[TB_ALBUM_FILES_FIELD_TYPE]

        item = {
            "uuid": item_uuid,
            "type": item_type,
            "shared": username != album_owner,
            "owner": album_owner,
            "content": {}
        }
        result.append(item)

    for o in items_shared:
        item = dynamo_obj_to_python_obj(o)
        item_uuid = item[TB_SHARED_WITH_ME_SK]
        item_type = item[TB_SHARED_WITH_ME_FIELD_TYPE]
        item_owner = item[TB_SHARED_WITH_ME_FIELD_OWNER]

        item = {
            "uuid": item_uuid,
            "type": item_type,
            "shared": True,
            "owner": item_owner,
            "content": {}
        }
        result.append(item)

    for o in result:
        if o['type'] == TB_ALBUM_FILES_FIELD_TYPE__ALBUM:
            o['content'] = album_uuid_to_album_metadata(o['owner'], o['uuid'])
        else:
            o['content'] = file_uuid_to_file_metadata(o['owner'], o['uuid'])
    

    return http_response(result, 200)