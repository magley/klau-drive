import base64
from dataclasses import dataclass
from datetime import datetime
import json
import os
from pathlib import Path
from typing import Dict, List
from src.lambdas.session import lambda_cli


@dataclass
class FileData():
    name: str
    type: str
    desc: str
    tags: List[str]
    size: int
    upload_date: datetime
    last_modified: datetime
    creation_date: datetime


# ------------------------------------------------------------------------------
#
# ------------------------------------------------------------------------------

LAMBDA_NAME = "upload_file"
LAMBDA_NAME_LS = "list_files"
BUCKET_NAME = "content"
TB_META_NAME = 'file_meta'
TB_META_PK = 'name'
TB_META_SK = None


# def upload_file_s3(fname: str, key: str):
#     create_bucket_if_not_exists(BUCKET_NAME)

#     s3_cli.upload_file(
#         Filename=fname,
#         Bucket=BUCKET_NAME,
#         Key=key
#     )


# def upload_file_dynamo(fname: str, desc: str, tags: List[str]):
#     create_table_if_not_exists(TB_META_NAME, TB_META_PK, TB_META_SK)

#     stat: os.stat_result = os.stat(fname)

#     size_in_bytes = stat.st_size
#     creation_time = datetime.fromtimestamp(stat.st_ctime)
#     modification_time = datetime.fromtimestamp(stat.st_mtime)
#     _, file_extension = os.path.splitext(fname)
#     just_name = Path(fname).stem

#     metadata = {
#         'name': just_name,
#         'size': size_in_bytes,
#         'creationDate': creation_time,
#         'modificationDate': modification_time,
#         'type': file_extension,
#         'desc': desc,
#         'tags': tags,
#         'uploadDate': datetime.now(),
#     }
#     item_data = d_json.dumps(metadata, as_dict=True)

#     dynamo_cli.put_item(
#         TableName=TB_META_NAME,
#         Item=item_data
#     )

# ------------------------------------------------------------------------------
#
# ------------------------------------------------------------------------------


# def list_files_nolambda() -> List[FileData]:
#     result = []

#     try:
#         response = s3_cli.list_objects(Bucket=BUCKET_NAME)
#     except s3_cli.exceptions.NoSuchBucket:
#         return result

#     contents = response.get('Contents')
#     if contents is None:
#         return result

#     for s3_file in contents:
#         dynamo_key = {TB_META_PK: s3_file['Key']}
#         dynamo_key = d_json.dumps(dynamo_key, as_dict=True)
#         dynamo_res = dynamo_cli.get_item(TableName=TB_META_NAME, Key=dynamo_key)
#         dynamo_item = d_json.loads(dynamo_res.get('Item'), as_dict=True)

#         item = FileData(
#             name=s3_file['Key'],
#             type=dynamo_item.get('type', ''),
#             desc=dynamo_item.get('desc', ''),
#             tags=dynamo_item.get('tags', []),
#             size=dynamo_item.get('size', 0),
#             upload_date=datetime.fromisoformat(dynamo_item.get('uploadDate', "")),
#             last_modified=datetime.fromisoformat(dynamo_item.get('modificationDate', "")),
#             creation_date=datetime.fromisoformat(dynamo_item.get('creationDate', "")),
#         )

#         result.append(item)

#     # TODO: Research if there's a way to get S3 to return items sorted by creation date
#     result = sorted(result, key=lambda item: item.upload_date, reverse=True)
#     return result


# def upload_file_nolambda(fname: str, desc: str, tags: List[str]):
#     key = Path(fname).stem
#     upload_file_s3(fname, key)
#     upload_file_dynamo(fname, desc, tags)


# ------------------------------------------------------------------------------
# LAMBDA
# ------------------------------------------------------------------------------


def make_metadata(fname: str, desc: str, tags: List[str]) -> Dict:
    stat: os.stat_result = os.stat(fname)
    size_in_bytes = stat.st_size
    creation_time = datetime.fromtimestamp(stat.st_ctime)
    modification_time = datetime.fromtimestamp(stat.st_mtime)
    _, file_extension = os.path.splitext(fname)
    just_name = Path(fname).stem

    metadata = {
        'name': just_name,
        'size': size_in_bytes,
        'creationDate': creation_time,
        'modificationDate': modification_time,
        'type': file_extension,
        'desc': desc,
        'tags': tags,
        'uploadDate': datetime.now(),
    }

    return metadata


def make_data_base64(fname: str) -> bytes:
    file_data_base64: bytes = None
    with open(fname, 'rb') as f:
        file_data_base64 = base64.b64encode(f.read()).decode("utf-8") 
    return file_data_base64 


def upload_file(fname: str, desc: str, tags: List[str]):
    metadata: Dict = make_metadata(fname, desc, str)
    data_b64: bytes = make_data_base64(fname)

    payload = {
        "body": {
            "metadata": metadata,
            "data": data_b64,
        }
    }

    payload_json = json.dumps(payload, default=str)

    lambda_cli.invoke(
        FunctionName=LAMBDA_NAME,
        Payload=payload_json
    )

def list_files():
    result = lambda_cli.invoke(
        FunctionName=LAMBDA_NAME_LS
    )

    p = json.loads(result['Payload'].read())
    print(p)
    body = p['body']

    res_items = [
        FileData(
            name=i['name'],
            type=i.get('type', ''),
            desc=i.get('desc', ''),
            tags=i.get('tags', []),
            size=i.get('size', 0),
            upload_date=datetime.fromisoformat(i.get('upload_date', "")),
            last_modified=datetime.fromisoformat(i.get('last_modified', "")),
            creation_date=datetime.fromisoformat(i.get('creation_date', "")),
        ) for i in body
    ]

    return res_items