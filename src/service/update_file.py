import base64
from dataclasses import dataclass
from datetime import datetime
import json
import os
from pathlib import Path
from typing import Dict, List
from src.service.session import BASE_URL
import requests


def make_metadata(name: str, desc: str, tags: List[str]) -> Dict:
    metadata = {
        'name': name,
        'desc': desc,
        'tags': tags,
        'modificationDate': datetime.now(),
    }

    return metadata


def make_data_base64(fname: str) -> bytes:
    file_data_base64: bytes = None
    with open(fname, 'rb') as f:
        file_data_base64 = base64.b64encode(f.read()).decode()
    return file_data_base64


def update_file(fname: str, desc: str, tags: List[str]):
    metadata: Dict = make_metadata(fname, desc, tags)
    #data_b64: bytes = make_data_base64(fname)

    payload = {
        "metadata": metadata,
        #"data": data_b64,
    }
    payload_json = json.dumps(payload, default=str)

    requests.put(f'{BASE_URL}/file', data=payload_json)