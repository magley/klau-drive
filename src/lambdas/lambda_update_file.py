from typing import Dict
from .common import *


def build_expression(data: Dict):
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


def lambda_update_file(event: Dict, context):
    body: Dict = json.loads(event['body'])
    metadata: Dict = body['metadata']

    primary_key = {
        CONTENT_METADATA_TB_PK: metadata['username'],
        CONTENT_METADATA_TB_SK: metadata['uuid']
    }

    # Get the whole object

    response = dynamo_cli.get_item(
        TableName=CONTENT_METADATA_TB_NAME,
        Key=python_obj_to_dynamo_obj(primary_key)
    )

    if 'Item' not in response:
        return http_response(f"No element under key {metadata['old_name']} exists!", 404)
    
    # Get all fields that were updated (except key fields!)

    new_obj: Dict = {}
    for k, v in metadata.items():
        if k not in ['username', 'uuid']:
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

    return http_response(None, 204)