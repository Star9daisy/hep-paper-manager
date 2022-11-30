import json
from dataclasses import dataclass, field

import requests
from rich import print

# ---------------------------------------------------------------------------- #
def query_database(database_id, token, source, cache=False):
    database_file = f"database-{database_id}.json"
    match source:
        case "local":
            print(f"-> Read local database")
            with open(database_file, "r") as f:
                database = json.load(f)
        case "remote":
            print(f"-> Fetch remote database")
            url = f"https://api.notion.com/v1/databases/{database_id}/query"

            payload = {
                "page_size": 100,
            }
            headers = {
                "accept": "application/json",
                "Notion-Version": "2022-06-28",
                "content-type": "application/json",
                "authorization": f"Bearer {token}",
            }
            response = requests.post(url, json=payload, headers=headers)
            database = json.loads(response.text)

            # print(f"Saved in {database_file}")

        case _:
            raise NameError("Choose source between local and remote!")

    return database


# ---------------------------------------------------------------------------- #
def to_property(property, value):
    match property:
        case "title" | "rich_text":
            return {property: [{"text": {"content": value}}]}

        case "number" | "url":

            return {property: value}

        case "select" | "status":
            return {property: {"name": value}}

        case "multi_select":
            return {"multi_select": [{"name": str(i)} for i in value]}


# ---------------------------------------------------------------------------- #
def to_relation(
    values: list[str],
    database_id: str,
    token: str,
    source: str,
):
    match source:
        case "local":
            with open(f"database-{database_id}.json", "r") as f:
                database = json.load(f)

        case "remote":
            database = query_database(database_id, token, source="remote")

        case _:
            raise NameError("Choose source between local and remote!")

    relation = {}
    for i in database["results"]:
        _name = i["properties"]["Name"]["title"][0]["plain_text"]
        _id = i["id"]
        relation[_name] = _id

    return {"relation": [{"id": relation[i]} for i in values if i in relation]}


# ---------------------------------------------------------------------------- #
@dataclass
class Paper:
    # base information
    title: str = ""
    authors: list[str] = field(default_factory=list)
    citations: int = 0
    published: str = ""
    tldr: str = ""
    source: str = ""

    # ids & links
    corpus_id: str = ""
    arxiv_id: str = ""
    semantic_link: str = ""
    inspire_link: str = ""

    # other
    bibtex: str = ""