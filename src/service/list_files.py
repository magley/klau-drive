from datetime import datetime
import json
from src.service.session import BASE_URL
import requests
import src.service.session as session
from src.service.upload_file import FileData


def list_files():
    payload = {
        "username": session.get_username()
    }
    payload_json = json.dumps(payload, default=str)

    r = requests.get(f'{BASE_URL}/file', data=payload_json)

    status_code = r.status_code

    if status_code == 200:
        body = r.json()
        res_items = [
            FileData(
                username=i['username'],
                uuid=i['uuid'],
                name=i['name'],
                type=i.get('type', ''),
                desc=i.get('desc', ''),
                tags=i.get('tags', []),
                size=i.get('size', 0),
                upload_date=datetime.fromisoformat(i.get('uploadDate', "")),
                last_modified=datetime.fromisoformat(i.get('modificationDate', "")),
                creation_date=datetime.fromisoformat(i.get('creationDate', "")),
            ) for i in body
        ]

        return res_items
    else:
        return []
        # print("TODO Error case", body)
