from __future__ import annotations

import json
from pathlib import Path

from hpm.notion import Client
from hpm.notion.objects import Page
from hpm.notion.objects.database import Database
import typer

app_dir = Path(typer.get_app_dir("hpm", force_posix=True))


# ---------------------------------------------------------------------------- #
def get_database(
    token: str,
    database_id: str,
    relink: bool = False,
    cache_dir: Path = app_dir,
    verbose: int = 0,
) -> Database:
    database_meta_file = cache_dir / f"{database_id}-meta.json"
    database_pages_file = cache_dir / f"{database_id}-pages.json"

    if not database_meta_file.exists() or not database_pages_file.exists() or relink:
        if verbose > 0:
            print(f"Linking to remote database ({database_id})...", end="", flush=True)
        # Retrieve database and save the response as a meta.json
        client = Client(token)
        response1 = client.retrieve_database(database_id)
        if response1.status_code != 200:
            raise Exception(response1.text)
        with open(database_meta_file, "w") as f:
            json.dump(response1.json(), f, indent=4)

        # Query database and save the response as a pages.json
        response2 = client.query_a_database(database_id)
        if response2.status_code != 200:
            raise Exception(response2.text)
        with open(database_pages_file, "w") as f:
            json.dump(response2.json(), f, indent=4)

        if verbose > 0:
            print("OK")

        database = Database.from_json(response1.json())
        database.pages = [Page.from_json(page) for page in response2.json()["results"]]

    else:
        if verbose > 0:
            print(f"Linking to local database ({database_id})...", end="", flush=True)
        # Read the meta.json and pages.json
        with open(database_meta_file, "r") as f:
            content1 = json.load(f)
        with open(database_pages_file, "r") as f:
            content2 = json.load(f)
        if verbose > 0:
            print("OK")

        database = Database.from_json(content1)
        database.pages = [Page.from_json(page) for page in content2["results"]]

    return database
