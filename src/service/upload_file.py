import base64
from dataclasses import dataclass
from datetime import datetime
import json
import os
from pathlib import Path
from typing import Dict, List
from src.service.session import lambda_cli


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


LAMBDA_NAME = "upload_file"
LAMBDA_NAME_LS = "list_files"
BUCKET_NAME = "content"
TB_META_NAME = 'file_meta'
TB_META_PK = 'name'
TB_META_SK = None

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
        file_data_base64 = base64.b64encode(f.read()).decode()
    return file_data_base64 


def upload_file(fname: str, desc: str, tags: List[str]):
    metadata: Dict = make_metadata(fname, desc, tags)
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

    body = p['body']
    if p['statusCode'] == 200:
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
    else:
        print("TODO Error case", body)