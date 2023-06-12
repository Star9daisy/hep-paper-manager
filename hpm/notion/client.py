from __future__ import annotations

import requests


class Client:
    def __init__(self, token: str):
        self.token = token

    def retrieve_database(self, database_id: str) -> requests.Response:
        url = f"https://api.notion.com/v1/databases/{database_id}"
        headers = {
            "accept": "application/json",
            "Notion-Version": "2022-06-28",
            "content-type": "application/json",
            "authorization": f"Bearer {self.token}",
        }

        return requests.get(url, headers=headers)

    def query_database(self, database_id: str) -> requests.Response:
        url = f"https://api.notion.com/v1/databases/{database_id}/query"
        payload = {"page_size": 100}
        headers = {
            "accept": "application/json",
            "Notion-Version": "2022-06-28",
            "content-type": "application/json",
            "authorization": f"Bearer {self.token}",
        }
        return requests.post(url, json=payload, headers=headers)

    def create_page(self, parent_id: str, properties: dict = {}) -> requests.Response:
        url = "https://api.notion.com/v1/pages"
        payload = {
            "parent": {
                "type": "database_id",
                "database_id": parent_id,
            },
            "properties": properties,
        }
        headers = {
            "accept": "application/json",
            "Notion-Version": "2022-06-28",
            "content-type": "application/json",
            "authorization": f"Bearer {self.token}",
        }
        return requests.post(url, json=payload, headers=headers)

    def retrieve_page(self, page_id: str) -> requests.Response:
        url = f"https://api.notion.com/v1/pages/{page_id}"
        headers = {
            "accept": "application/json",
            "Notion-Version": "2022-06-28",
            "content-type": "application/json",
            "authorization": f"Bearer {self.token}",
        }
        return requests.get(url, headers=headers)

    def update_page(self, page_id: str, properties: dict = {}) -> requests.Response:
        url = f"https://api.notion.com/v1/pages/{page_id}"
        payload = {
            "properties": properties,
        }
        headers = {
            "accept": "application/json",
            "Notion-Version": "2022-06-28",
            "content-type": "application/json",
            "authorization": f"Bearer {self.token}",
        }
        return requests.patch(url, json=payload, headers=headers)

    def archive_page(self, page_id: str) -> requests.Response:
        url = f"https://api.notion.com/v1/pages/{page_id}"
        payload = {
            "archived": True,
        }
        headers = {
            "accept": "application/json",
            "Notion-Version": "2022-06-28",
            "content-type": "application/json",
            "authorization": f"Bearer {self.token}",
        }
        return requests.patch(url, json=payload, headers=headers)

    def restore_page(self, page_id: str) -> requests.Response:
        url = f"https://api.notion.com/v1/pages/{page_id}"
        payload = {
            "archived": False,
        }
        headers = {
            "accept": "application/json",
            "Notion-Version": "2022-06-28",
            "content-type": "application/json",
            "authorization": f"Bearer {self.token}",
        }
        return requests.patch(url, json=payload, headers=headers)
