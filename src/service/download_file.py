import json
from src.service.session import BASE_URL
import requests
import src.service.session as session
import base64


def download_file(file_uuid: str, owner: str) -> bytes:
    payload = {
        "file_uuid": file_uuid,
        "owner": owner
    }
    payload_json = json.dumps(payload, default=str)
    header = {'Authorization': f'Bearer {session.get_jwt()}'}
    result: requests.Response = requests.get(f'{BASE_URL}/file-download', data=payload_json, headers=header)

    if not result.ok:
        print(result, result.json())

    return base64.b64decode(result.json())