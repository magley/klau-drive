from typing import Dict
from common import *


"""
awslocal lambda create-function --function-name list_files --zip-file fileb://list_files.zip --runtime python3.9 --handler lambda_list_files.lambda_list_files --role arn:aws:iam::000000000000:role/LambdaBasic
awslocal lambda update-function-configuration --function-name list_files --timeout 180
awslocal lambda update-function-code --function-name list_files --zip-file fileb://list_files.zip
awslocal lambda invoke --function-name list_files ./out.json
"""

def lambda_list_files(event: Dict, context):
    result = []

    try:
        response = s3_cli.list_objects(Bucket=CONTENT_BUCKET_NAME)
    except s3_cli.exceptions.NoSuchBucket:
        return {
            "body": result
        }

    contents = response.get('Contents')
    if contents is None:
        return {
            "body": result
        }

    for s3_file in contents:
        dynamo_key = {CONTENT_METADATA_TB_PK: s3_file['Key']}
        dynamo_key = python_obj_to_dynamo_obj(dynamo_key)
        dynamo_res = dynamo_cli.get_item(TableName=CONTENT_METADATA_TB_NAME, Key=dynamo_key)
        dynamo_item = dynamo_obj_to_python_obj(dynamo_res.get('Item'))

        item = {
            "name":s3_file['Key'],
            "type":dynamo_item.get('type', ''),
            "desc":dynamo_item.get('desc', ''),
            "tags":dynamo_item.get('tags', []),
            "size":dynamo_item.get('size', 0),
            "upload_date":dynamo_item.get('uploadDate', ""),
            "last_modified":dynamo_item.get('modificationDate', ""),
            "creation_date":dynamo_item.get('creationDate', ""),
        }

        result.append(item)
    result = sorted(result, key=lambda item: item['upload_date'], reverse=True)
    
    return {
        "body": result
    }