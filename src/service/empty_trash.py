from src.service.session import BASE_URL
import requests
import src.service.session as session


def empty_trash():
    header = {'Authorization': f'Bearer {session.get_jwt()}'}
    result: requests.Response = requests.put(f'{BASE_URL}/gc', headers=header)

    print(result, result.json())