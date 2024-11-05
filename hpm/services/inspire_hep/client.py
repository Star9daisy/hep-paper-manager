from __future__ import annotations
import requests


class InspireHEP:
    def __init__(self) -> None:
        self.base_url = "https://inspirehep.net/api"

    def get(self, identifier_type: str, identifier_value: str) -> dict:
        url = f"{self.base_url}/{identifier_type}/{identifier_value}"
        response = requests.get(url)
        response.raise_for_status()

        return response.json()

    def get_paper(self, identifier_value: str) -> dict:
        if "." in identifier_value or "/" in identifier_value:
            return self.get("arxiv", identifier_value)
        else:
            return self.get("literature", identifier_value)

    def get_author(self, identifier_value: str) -> dict:
        return self.get("authors", identifier_value)

    def get_job(self, identifier_value: str) -> dict:
        return self.get("jobs", identifier_value)
