import requests
from requests import Response


def create_page(token: str, parent: dict, properties: dict) -> Response:
    url = "https://api.notion.com/v1/pages"
    payload = {
        "parent": parent,
        "properties": properties,
    }
    headers = {
        "accept": "application/json",
        "Notion-Version": "2022-06-28",
        "content-type": "application/json",
        "authorization": f"Bearer {token}",
    }

    return requests.post(url, json=payload, headers=headers)
