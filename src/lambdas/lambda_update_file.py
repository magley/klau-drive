import base64
import io

from .common import *


def save_backup(username: str, uuid: str):
    metadata = file_uuid_to_file_metadata(username, uuid)

    dynamo_cli.put_item(
        TableName=TB_LAST_VALID_CONTENT_NAME,
        Item=python_obj_to_dynamo_obj(metadata)
    )


def discard_backup(uuid: str):
    dynamo_cli.delete_item(
        TableName=TB_LAST_VALID_CONTENT_NAME,
        Key=python_obj_to_dynamo_obj({
            TB_LAST_VALID_CONTENT_PK: uuid
        })
    )


def fetch_backup(uuid: str):
    statement = f"""
        SELECT * FROM {TB_LAST_VALID_CONTENT_NAME}
        WHERE
            {TB_LAST_VALID_CONTENT_PK}=?
    """
    parameters = python_obj_to_dynamo_obj([uuid])

    response = dynamo_cli.execute_statement(    
        Statement=statement,
        Parameters=parameters
    )

    for o in response['Items']:
        obj = dynamo_obj_to_python_obj(o)
        return obj # There should be only 1.
    return {}   


def rollback_backup(uuid: str):
    old_obj = fetch_backup(uuid)

    # Update real metadata with old copy

    new_obj: dict = {}
    for k, v in old_obj.items():
        if k not in [CONTENT_METADATA_TB_PK, CONTENT_METADATA_TB_SK]:
            new_obj[k] = v
        
    update_expression, expression_attr_names, expression_attr_vals = build_expression(new_obj)
    dynamo_cli.update_item(
        Key=python_obj_to_dynamo_obj({
            CONTENT_METADATA_TB_PK: old_obj[CONTENT_METADATA_TB_PK],
            CONTENT_METADATA_TB_SK: old_obj[CONTENT_METADATA_TB_SK]
        }),
        TableName=CONTENT_METADATA_TB_NAME,
        UpdateExpression=update_expression,
        ExpressionAttributeNames=expression_attr_names,
        ExpressionAttributeValues=python_obj_to_dynamo_obj(expression_attr_vals)
    )


def build_expression(data: dict):
    expression_attr_names = {}
    expression_attr_vals = {}
    for i, (k, v) in enumerate(data.items()):
        expression_attr_names[f'#f{i}'] = k
        expression_attr_vals[f':f{i}'] = v
    update_expression = "SET "
    for i in range(len(expression_attr_vals)):
        update_expression += f'#f{i} = :f{i}, '
    update_expression = update_expression[:-2]

    return update_expression, expression_attr_names, expression_attr_vals


def lambda_update_file(event: dict, context):
    body: dict = json.loads(event['body'])
    headers: dict = event['headers']

    username: str = jwt_decode(headers)
    if not user_exists(username):
        return http_response("Forbidden", 401)
    
    metadata: dict = body['metadata']

    if not has_write_accesss(username, metadata[CONTENT_METADATA_TB_SK]):
        return http_response("You don't own this.", 404)

    primary_key = {
        CONTENT_METADATA_TB_PK: metadata[CONTENT_METADATA_TB_PK],
        CONTENT_METADATA_TB_SK: metadata[CONTENT_METADATA_TB_SK]
    }

    # Get the whole object

    response = dynamo_cli.get_item(
        TableName=CONTENT_METADATA_TB_NAME,
        Key=python_obj_to_dynamo_obj(primary_key)
    )

    if 'Item' not in response:
        return http_response(f"No element under key {metadata['name']} exists!", 404)
    
    if filename_used(metadata['uuid'], metadata['name'], username, body['album_uuid']):
        return http_response("Can't update, filename in use!", 400)
    
    # Update metadata

    file_uuid: str = metadata[CONTENT_METADATA_TB_SK]

    save_backup(username, file_uuid)
    
    # Get all fields that were updated (except key fields!)

    new_obj: dict = {}
    for k, v in metadata.items():
        if k not in [CONTENT_METADATA_TB_PK, CONTENT_METADATA_TB_SK]:
            new_obj[k] = v

    # Build update expression 

    update_expression, expression_attr_names, expression_attr_vals = build_expression(new_obj)

    # Apply updating

    dynamo_cli.update_item(
        Key=python_obj_to_dynamo_obj(primary_key),
        TableName=CONTENT_METADATA_TB_NAME,
        UpdateExpression=update_expression,
        ExpressionAttributeNames=expression_attr_names,
        ExpressionAttributeValues=python_obj_to_dynamo_obj(expression_attr_vals)
    )

    # Update the contents

    success = True
    if 'data' in body:
        try:
            data: bytes = base64.b64decode(body['data'])

            s3_cli.upload_fileobj(
                Fileobj=io.BytesIO(data),
                Bucket=CONTENT_BUCKET_NAME,
                Key=metadata[CONTENT_METADATA_TB_SK]
            )
        except Exception as e:
            rollback_backup(file_uuid)
            success = False  

    discard_backup(file_uuid)

    if not success:
        return http_response("Failed to upload, fixing consistency.", 500)
    else:
        send_email(username, f"You have just updated a file: {metadata['uuid']}", "File updated")
        return http_response(None, 204)
