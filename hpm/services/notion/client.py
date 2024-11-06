from __future__ import annotations

import os

import requests
from typeguard import typechecked

from .objects.database_properties import DatabaseProperty
from .objects.page_properties import PageProperty


@typechecked
class Notion:
    def __init__(self, token: str | None = None) -> None:
        self.base_url = "https://api.notion.com/v1"
        self.token = token or os.getenv("NOTION_ACCESS_TOKEN_FOR_HPM")
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28",
        }

    def create_page(self, parent_id: str, properties: dict[str, PageProperty]) -> dict:
        url = f"{self.base_url}/pages"
        body = {
            "parent": {"database_id": parent_id},
            "properties": {k: v.as_dict() for k, v in properties.items()},
        }
        response = requests.post(url, json=body, headers=self.headers)

        if response.status_code != 200:
            raise ValueError(f"Failed to create page: {response.json()}")

        return response.json()

    def retrieve_page(self, id: str) -> dict:
        url = f"{self.base_url}/pages/{id}"
        response = requests.get(url, headers=self.headers)

        if response.status_code != 200:
            raise ValueError(f"Failed to retrieve page: {response.json()}")

        return response.json()

    def update_page(self, id: str, properties: dict[str, PageProperty]) -> dict:
        url = f"{self.base_url}/pages/{id}"
        body = {"properties": {k: v.as_dict() for k, v in properties.items()}}
        response = requests.patch(url, json=body, headers=self.headers)

        if response.status_code != 200:
            raise ValueError(f"Failed to update page: {response.json()}")

        return response.json()

    def archive_page(self, id: str) -> None:
        url = f"{self.base_url}/pages/{id}"
        body = {"archived": True}
        response = requests.patch(url, json=body, headers=self.headers)

        if response.status_code != 200:
            raise ValueError(f"Failed to archive page: {response.json()}")

    def query_database(
        self, id: str, start_cursor: str | None = None, page_size: int = 100
    ) -> dict:
        url = f"{self.base_url}/databases/{id}/query"
        body = {"page_size": page_size}

        if start_cursor:
            body["start_cursor"] = start_cursor

        response = requests.post(url, json=body, headers=self.headers)

        if response.status_code != 200:
            raise ValueError(f"Failed to query database: {response.json()}")

        return response.json()

        # while True:
        #     response = requests.post(url, json=payload, headers=self.headers)

        #     if response.status_code != 200:
        #         raise ValueError(f"Failed to query database: {response.json()}")

        #     data = response.json()
        #     yield data

        #     if not data["has_more"]:
        #         break

        #     payload["start_cursor"] = data["next_cursor"]

    def retrieve_database(self, id: str) -> dict:
        url = f"{self.base_url}/databases/{id}"
        response = requests.get(url, headers=self.headers)

        if response.status_code != 200:
            raise ValueError(f"Failed to retrieve database: {response.json()}")

        return response.json()

    def search_database(self, title: str | None = None) -> dict:
        url = f"{self.base_url}/search"
        body = {
            "query": title or "",
            "filter": {
                "value": "database",
                "property": "object",
            },
            "sort": {
                "direction": "ascending",
                "timestamp": "last_edited_time",
            },
        }
        response = requests.post(url, json=body, headers=self.headers)

        if response.status_code != 200:
            raise ValueError(f"Failed to search database: {response.json()}")

        return response.json()

    def create_database(
        self,
        parent_id: str,
        title: str,
        properties: dict[str, DatabaseProperty],
    ) -> dict:
        url = f"{self.base_url}/databases"
        body = {
            "parent": {"type": "page_id", "page_id": parent_id},
            "title": [{"type": "text", "text": {"content": title, "link": None}}],
            "properties": {name: prop.as_dict() for name, prop in properties.items()},
        }
        response = requests.post(url, json=body, headers=self.headers)

        if response.status_code != 200:
            raise ValueError(f"Failed to create database: {response.json()}")

        return response.json()

    def archive_database(self, id: str) -> None:
        url = f"{self.base_url}/databases/{id}"
        body = {"archived": True}
        response = requests.patch(url, json=body, headers=self.headers)

        if response.status_code != 200:
            raise ValueError(f"Failed to archive database: {response.json()}")
