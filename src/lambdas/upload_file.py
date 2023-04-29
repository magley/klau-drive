from datetime import datetime
import os
from pathlib import Path
from typing import List
from dynamodb_json import json_util as d_json
from src.lambdas.session import s3_cli, s3_res, dynamo_cli

class FileData():
    def __init__(self, name: str, type: str, desc: str, tags: List[str], size: int, upload_date: datetime, last_modified: datetime, creation_date: datetime):
        self.name = name
        self.type = type
        self.desc = desc
        self.tags = tags[:]
        self.upload_date = upload_date
        self.last_modified = last_modified
        self.creation_date = creation_date
        self.size = size

    def __str__(self) -> str:
        return f"({self.name} {self.type} '{self.desc}' {self.tags} {self.size}B {self.upload_date} {self.creation_date} {self.last_modified})"


# ------------------------------------------------------------------------------
#
# ------------------------------------------------------------------------------

BUCKET_NAME = "content"
TB_META_NAME = 'file_meta'
TB_META_PK = 'name'
TB_META_SK = None


def upload_file_s3(fname: str, key: str):
    s3_cli.upload_file(
        Filename=fname,
        Bucket=BUCKET_NAME,
        Key=key
    )


def upload_file_dynamo(fname: str, desc: str, tags: List[str]):
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
    item_data = d_json.dumps(metadata, as_dict=True)

    dynamo_cli.put_item(
        TableName=TB_META_NAME,
        Item=item_data
    )

# ------------------------------------------------------------------------------
#
# ------------------------------------------------------------------------------


def list_files() -> List[FileData]:
    response = s3_cli.list_objects(Bucket=BUCKET_NAME)
    result = []

    contents = response.get('Contents')
    if contents is None:
        return result

    for s3_file in contents:
        dynamo_key = {TB_META_PK: s3_file['Key']}
        dynamo_key = d_json.dumps(dynamo_key, as_dict=True)
        dynamo_res = dynamo_cli.get_item(
            TableName=TB_META_NAME, Key=dynamo_key)
        dynamo_item = d_json.loads(dynamo_res.get('Item'), as_dict=True)

        # item = {}
        # item['s3_Key'] = s3_file['Key']
        # item['s3_LastModified'] = s3_file['LastModified']
        # item['db_uploadDate'] = dynamo_item['uploadDate']
        # item['db_creationDate'] = dynamo_item['creationDate']
        # item['db_modificationDate'] = dynamo_item['modificationDate']
        # item['db_size'] = dynamo_item['size']
        # item['db_type'] = dynamo_item['type']
        # item['db_desc'] = dynamo_item['desc']
        # item['db_tags'] = dynamo_item['tags']

        item = FileData(
            name=s3_file['Key'],
            type=dynamo_item['type'],
            desc=dynamo_item['desc'],
            tags=dynamo_item['tags'],
            size=dynamo_item['size'],
            upload_date=dynamo_item['uploadDate'],
            last_modified=s3_file['LastModified'],
            creation_date=dynamo_item['creationDate']
        )

        result.append(item)

    # TODO: Research if there's a way to get S3 to return items sorted by creation date
    result = sorted(result, key=lambda item: item.upload_date, reverse=True)
    return result


def upload_file(fname: str, desc: str, tags: List[str]):
    key = Path(fname).stem
    upload_file_s3(fname, key)
    upload_file_dynamo(fname, desc, tags)


# Init()
# UploadFile("./upload_file.py", "First file", ['python', 'aws', 'localstack'])
# for file in ListFiles():
#     print(json.dumps(file, indent=2, default=str))
