from .common import *


def lambda_collect_garbage(event: dict, context):
    return http_response("No content", 204)