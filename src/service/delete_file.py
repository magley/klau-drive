import json
from src.service.session import BASE_URL
import requests
import src.service.session as session


def delete_file(file_uuid: str, album_uuid: str) -> requests.Response:
    payload = {
        "uuid": file_uuid,
        "album_uuid": album_uuid,
    }
    payload_json = json.dumps(payload, default=str)

    header = {'Authorization': f'Bearer {session.get_jwt()}'}
    result: requests.Response = requests.delete(f'{BASE_URL}/file', data=payload_json, headers=header)

    return result