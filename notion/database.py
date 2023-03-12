import requests
from requests import Response


def retrieve_database(token: str, database_id: str) -> Response:
    url = f"https://api.notion.com/v1/databases/{database_id}"
    headers = {
        "accept": "application/json",
        "Notion-Version": "2022-06-28",
        "content-type": "application/json",
        "authorization": f"Bearer {token}",
    }

    return requests.get(url, headers=headers)


def query_database(token: str, database_id: str, sorts: list | None = None) -> Response:
    url = f"https://api.notion.com/v1/databases/{database_id}/query"

    if sorts:
        payload = {"page_size": 100, "sorts": sorts}
    else:
        payload = {"page_size": 100}

    headers = {
        "accept": "application/json",
        "Notion-Version": "2022-06-28",
        "content-type": "application/json",
        "authorization": f"Bearer {token}",
    }

    return requests.post(url, json=payload, headers=headers)
