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


def stop_share(owner: str, uuid: str, username: str):
    payload = {
        "owner": owner,
        "uuid": uuid,
        "username": username
    }
    payload_json = json.dumps(payload, default=str)

    header = {'Authorization': f'Bearer {session.get_jwt()}'}
    r = requests.put(f'{session.BASE_URL}/share-stop', data=payload_json, headers=header)
 
    if not r.ok:
        print(r.json())
    
    return None


def get_shared_with_me():
    """
        `username` - Self
        `owner` - Owner of the actual item
        `uuid` - UUID.
        `is_album` - 'folder' or 'file'
    """
    header = {'Authorization': f'Bearer {session.get_jwt()}'}
    result: requests.Response = requests.get(f'{session.BASE_URL}/get-shared', headers=header)

    if not result.ok:
        print(result)

    return result.json()


def get_my_sharing(with_whom_its_shared: str):
    """
        `owner` - self
        `username` - with whom it's shared
        `uuid` - UUID.
        `type` - 'folder' or 'file'
    """
    payload = {
        "username": with_whom_its_shared
    }
    payload_json = json.dumps(payload, default=str)

    header = {'Authorization': f'Bearer {session.get_jwt()}'}
    result: requests.Response = requests.get(f'{session.BASE_URL}/get-sharing', data=payload_json, headers=header)

    if not result.ok:
        print(result)

    return result.json()