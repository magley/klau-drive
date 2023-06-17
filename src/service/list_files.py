from datetime import datetime
import json
from src.service.session import BASE_URL
import requests
import src.service.session as session
from src.service.upload_file import FileData


def list_files():
    payload = {
        "album_uuid": f"{session.get_username()}_root",
    }
    payload_json = json.dumps(payload, default=str)

    header = {'Authorization': f'Bearer {session.get_jwt()}'}
    r = requests.get(f'{BASE_URL}/file', data=payload_json, headers=header)

    status_code = r.status_code

    if status_code == 200:
        body = r.json()
        res_items = []

        for item in body:
            if item['type'] == 'file':
                i = item['content']
                res_items.append(
                    FileData(
                        username=i['username'],
                        uuid=item['uuid'],
                        name=i['name'],
                        type=i.get('type', ''),
                        desc=i.get('desc', ''),
                        tags=i.get('tags', []),
                        size=i.get('size', 0),
                        upload_date=datetime.fromisoformat(i.get('uploadDate', "")),
                        last_modified=datetime.fromisoformat(i.get('modificationDate', "")),
                        creation_date=datetime.fromisoformat(i.get('creationDate', "")),
                    )
                )
            else:
                i = item['content']
                res_items.append(FileData(
                        username=i['username'],
                        uuid=item['uuid'],
                        name=i['name'],
                        type='Album',
                        desc=i.get('desc', ''),
                        tags=i.get('tags', []),
                        size=i.get('size', 0),
                        upload_date=datetime.fromisoformat(i.get('uploadDate', datetime.now().isoformat())),
                        last_modified=datetime.fromisoformat(i.get('modificationDate', datetime.now().isoformat())),
                        creation_date=datetime.fromisoformat(i.get('creationDate', datetime.now().isoformat())),
                    )
                )

        return res_items
    else:
        return []
        # print("TODO Error case", body)