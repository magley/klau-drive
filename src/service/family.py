import json
import requests
import src.service.session as session


def approve(username: str):
    print(f"Sharing everything with user {username}")
    payload = {
        "sharing_to_username": username,
    }
    payload_json = json.dumps(payload, default=str)
    header = {'Authorization': f'Bearer {session.get_jwt()}'}
    r = requests.put(f'{session.BASE_URL}/family/approve', data=payload_json, headers=header)
    if not r.ok:
        print(r, r.json())


def reject(username: str):
    print(f"Reject family user {username}")
    payload = {
        "sharing_to_username": username,
    }
    payload_json = json.dumps(payload, default=str)
    header = {'Authorization': f'Bearer {session.get_jwt()}'}
    r = requests.put(f'{session.BASE_URL}/family/reject', data=payload_json, headers=header)
    if not r.ok:
        print(r, r.json())


def get_family_verifications():
    header = {'Authorization': f'Bearer {session.get_jwt()}'}
    r: requests.Response = requests.get(f'{session.BASE_URL}/family', headers=header)
    if not r.ok:
        print(r, r.json())
    return r.json()
