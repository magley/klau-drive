import json
from src.service.session import BASE_URL
import requests
import src.service.session as session
import uuid


def get_albums() -> requests.Response:
    """
        Returns a list of objects with the fields:
        `name` - Name of the album
        `username` - Owner of the album (should be the same for all of them)
        `album_uuid` - UUID of the album.
    """
    header = {'Authorization': f'Bearer {session.get_jwt()}'}
    result: requests.Response = requests.get(f'{BASE_URL}/album', headers=header)

    if not result.ok:
        print(result)

    return result.json()