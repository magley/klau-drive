import json
from src.service.session import BASE_URL
import requests
import src.service.session as session


def move_file(album_old_uuid: str, album_new_uuid: str, uuid: str, should_cut: bool) -> requests.Response:
    payload = {
        "album_old_uuid": album_old_uuid,
        "album_new_uuid": album_new_uuid,
        "uuid": uuid,
        "cut": should_cut
    }
    payload_json = json.dumps(payload, default=str)

    header = {'Authorization': f'Bearer {session.get_jwt()}'}
    result: requests.Response = requests.put(f'{BASE_URL}/move', data=payload_json, headers=header)

    if not result.ok:
        print(result, result.json())

    return result