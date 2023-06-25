import base64
import io

from .common import *


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
        return http_response(f"No element under key {metadata['old_name']} exists!", 404)
    
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

    if 'data' in body:
        data: bytes = base64.b64decode(body['data'])

        s3_cli.upload_fileobj(
            Fileobj=io.BytesIO(data),
            Bucket=CONTENT_BUCKET_NAME,
            Key=metadata[CONTENT_METADATA_TB_SK]
        )

    return http_response(None, 204)