from typing import Dict
from .common import *


def lambda_update_file(event: Dict, context):
    body: Dict = json.loads(event['body'])
    metadata: Dict = body['metadata']
    metadata_dynamojson: str = python_obj_to_dynamo_obj(metadata)

    return http_response(None, 204)