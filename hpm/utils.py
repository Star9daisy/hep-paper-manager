import json
from dataclasses import dataclass, field

import requests


# ---------------------------------------------------------------------------- #
def query_a_database(database_id, token):
    url = f"https://api.notion.com/v1/databases/{database_id}/query"

    payload = {"page_size": 100}
    headers = {
        "accept": "application/json",
        "Notion-Version": "2022-06-28",
        "content-type": "application/json",
        "authorization": f"Bearer {token}",
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 200:
        print(response.text)
        raise LookupError(f"✘ Something wrong")

    # ------------------------------------------------------------------------ #
    database = json.loads(response.text)
    # with open(f"database_{database_id}.json", "w") as f:
    #     json.dump(database, f, indent=4)

    return database


# find page ids for names
def find_relation_ids(token, database_id, names):
    database = query_a_database(
        token=token,
        database_id=database_id,
    )

    ids = []
    for result in database["results"]:
        _id = result["id"]
        _title = ""
        for content in result["properties"].values():
            if content["type"] == "title":
                _title = content["title"][0]["text"]["content"]
                break
        if _title in names:
            ids.append(_id)
    return ids
