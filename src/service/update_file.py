import base64
from dataclasses import dataclass
from datetime import datetime
import json
import os
from pathlib import Path
from typing import Dict, List
from src.service.session import BASE_URL
import requests
import boto3
from os import environ
import src.service.session as session


def make_metadata(username: str, uuid: str, new_name: str, new_desc: str, new_tags: List[str]) -> Dict:
    metadata = {
        'username': username,
        'uuid': uuid,
        'name': new_name,
        'desc': new_desc,
        'tags': new_tags,
        'modificationDate': datetime.now(),
    }

    return metadata


def make_data_base64(fname: str) -> bytes:
    file_data_base64: bytes = None
    with open(fname, 'rb') as f:
        file_data_base64 = base64.b64encode(f.read()).decode()
    return file_data_base64



def update_file(uuid: str, new_name: str, new_desc: str, new_tags: List[str]):   
    metadata: Dict = make_metadata(session.get_username(), uuid, new_name, new_desc, new_tags)
    payload = {
        "metadata": metadata
    }
    payload_json = json.dumps(payload, default=str)
    requests.put(f'{BASE_URL}/file', data=payload_json)