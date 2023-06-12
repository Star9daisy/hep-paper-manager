from __future__ import annotations

import requests

from .objects import Page


class Client:
    def __init__(self, token: str):
        self.token = token

    # def retrieve_database(self, database_id: str) -> Database:
    #     url = f"https://api.notion.com/v1/databases/{database_id}"
    #     headers = {
    #         "accept": "application/json",
    #         "Notion-Version": "2022-06-28",
    #         "content-type": "application/json",
    #         "authorization": f"Bearer {self.token}",
    #     }

    #     response = requests.get(url, headers=headers)
    #     if response.status_code != 200:
    #         raise Exception(response.text)
    #     else:
    #         return Database.from_json(response.json())

    # def query_database(self, database_id: str) -> list[Page]:
    #     url = f"https://api.notion.com/v1/databases/{database_id}/query"
    #     payload = {"page_size": 100}
    #     headers = {
    #         "accept": "application/json",
    #         "Notion-Version": "2022-06-28",
    #         "content-type": "application/json",
    #         "authorization": f"Bearer {self.token}",
    #     }
    #     response = requests.post(url, json=payload, headers=headers)

    #     if response.status_code != 200:
    #         raise Exception(response.text)
    #     else:
    #         pages = [Page.from_json(page) for page in response.json()["results"]]
    #         return pages

    def create_page(self, page: Page) -> requests.Response:
        url = "https://api.notion.com/v1/pages"
        payload = {
            "parent": {
                "type": "database_id",
                "database_id": page.parent_id,
            },
            "properties": page.properties_to_dict(),
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

    def update_page(self, page: Page) -> requests.Response:
        url = f"https://api.notion.com/v1/pages/{page.id}"
        payload = {
            "properties": page.properties_to_dict(),
        }
        headers = {
            "accept": "application/json",
            "Notion-Version": "2022-06-28",
            "content-type": "application/json",
            "authorization": f"Bearer {self.token}",
        }
        return requests.patch(url, json=payload, headers=headers)

    def archive_page(self, page: Page) -> requests.Response:
        url = f"https://api.notion.com/v1/pages/{page.id}"
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

    def restore_page(self, page: Page) -> requests.Response:
        url = f"https://api.notion.com/v1/pages/{page.id}"
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
