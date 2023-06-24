import json
import requests
import src.service.session as session


def share(username: str, uuid: str, is_album: bool):
    print(f"Sharing {uuid} which is an album ({is_album}) with user {username}")

    payload = {
        "uuid": uuid,
        "username": username,
        "is_album": is_album
    }
    payload_json = json.dumps(payload, default=str)

    header = {'Authorization': f'Bearer {session.get_jwt()}'}
    r = requests.put(f'{session.BASE_URL}/share', data=payload_json, headers=header)
    status = r.status_code

    if status == 400:
        print(r.json())
    
    return None
