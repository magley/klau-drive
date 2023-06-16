import json
from src.service.session import BASE_URL
import requests
import src.service.session as session


def delete_file(file_uuid: str) -> requests.Response:
    payload = {
        "album_uuid": f"{session.get_username()}_root",
        "uuid": file_uuid,
    }
    payload_json = json.dumps(payload, default=str)

    header = {'Authorization': f'Bearer {session.get_jwt()}'}
    result: requests.Response = requests.delete(f'{BASE_URL}/file', data=payload_json, headers=header)

    return result