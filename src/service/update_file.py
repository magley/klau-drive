import base64
from dataclasses import dataclass
from datetime import datetime
import json
import os
from pathlib import Path
from typing import List
from src.service.session import BASE_URL
import requests
import boto3
from os import environ
import src.service.session as session
import src.service.upload_file as upload_file


def make_metadata(username: str, uuid: str, new_name: str, new_desc: str, new_tags: List[str]) -> dict:
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



def update_file(uuid: str, new_name: str, new_desc: str, new_tags: List[str], new_fname: str | None):   
    metadata: dict = make_metadata(session.get_username(), uuid, new_name, new_desc, new_tags)
    payload = {}

    if new_fname is not None and new_fname != "":
        data_b64: bytes = make_data_base64(new_fname)
        payload['data'] = data_b64

        metadata_2: dict = upload_file.make_metadata(new_fname, new_desc, new_tags)
        metadata['size'] = metadata_2['size']
        metadata['type'] = metadata_2['type']

    payload['metadata'] = metadata

    payload_json = json.dumps(payload, default=str)

    print(f"Upading http://localhost:4566/content/{metadata['uuid']}")

    header = {'Authorization': f'Bearer {session.get_jwt()}'}
    requests.put(f'{BASE_URL}/file', data=payload_json, headers=header)