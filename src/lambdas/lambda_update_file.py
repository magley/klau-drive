from typing import Dict
from .common import *


def lambda_update_file(event: Dict, context):
    body: Dict = json.loads(event['body'])
    metadata: Dict = body['metadata']

    # TODO: This doesn't change the name. We can't change it normally since 
    # it's a partition key. Change the dynamodb structure!

    old_key = {
        CONTENT_METADATA_TB_PK: metadata['old_name']
    }

    key = {
        CONTENT_METADATA_TB_PK: metadata['name']
    }

    # Get everything from the old object

    response = dynamo_cli.get_item(
        TableName=CONTENT_METADATA_TB_NAME,
        Key=python_obj_to_dynamo_obj(old_key)
    )

    if 'Item' not in response:
        return http_response(f"No element under key {metadata['old_name']} exists!", 404)

    new_obj: Dict = {}
    for k, v in metadata.items():
        if k not in ['name', 'old_name']:
            new_obj[k] = v

    # Update the object

    expression_attr_names = {}
    expression_attr_vals = {}
    for i, (k, v) in enumerate(new_obj.items()):
        expression_attr_names[f'#f{i}'] = k
        expression_attr_vals[f':f{i}'] = v
    update_expression = "SET "
    for i in range(len(expression_attr_vals)):
        update_expression += f'#f{i} = :f{i}, '
    update_expression = update_expression[:-2]

    dynamo_cli.update_item(
        Key=python_obj_to_dynamo_obj(key),
        TableName=CONTENT_METADATA_TB_NAME,
        UpdateExpression=update_expression,
        ExpressionAttributeNames=expression_attr_names,
        ExpressionAttributeValues=python_obj_to_dynamo_obj(expression_attr_vals)
    )

    #########

    # Update the file content (if possible)

    ## TODO: Split into 2 functions, one for meta only, other for file

    # data: bytes = base64.b64decode(body['data'])

    # dynamo_cli.put_item(
    #     TableName=CONTENT_METADATA_TB_NAME,
    #     Item=metadata_dynamojson
    # )

    # s3_cli.upload_fileobj(
    #     Fileobj=io.BytesIO(data),
    #     Bucket=CONTENT_BUCKET_NAME,
    #     Key=metadata['name']
    # )

    return http_response(None, 204)