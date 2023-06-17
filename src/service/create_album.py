import json
from src.service.session import BASE_URL
import requests
import src.service.session as session
import uuid


def create_album(parent_uuid: str, name: str) -> requests.Response:
    payload = {
        "parent_uuid": f"{session.get_username()}_root",
        "uuid": str(uuid.uuid4()),
        "name": name
    }
    payload_json = json.dumps(payload, default=str)

    header = {'Authorization': f'Bearer {session.get_jwt()}'}
    result: requests.Response = requests.post(f'{BASE_URL}/album', data=payload_json, headers=header)

    if not result.ok:
        print(result)

    return result