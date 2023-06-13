import json
import os
from importlib import import_module
from pathlib import Path
from typing import Optional

import typer
import yaml
from rich import print
from rich.panel import Panel
from typing_extensions import Annotated

from hpm import CACHED_PAPERS_DIR
from hpm.engines.inspire import Inspire, Paper
from hpm.notion.client import Client
from hpm.notion.objects import Database, Page
from hpm.notion.properties import *

from . import __app_name__, __app_version__

# ---------------------------------------------------------------------------- #
app = typer.Typer(
    context_settings={"help_option_names": ["-h", "--help"]},
    add_completion=False,
)
app_dir = Path(typer.get_app_dir("hpm", force_posix=True))
app_dir.mkdir(parents=True, exist_ok=True)

cached_papers_dir = CACHED_PAPERS_DIR
cached_papers_dir.mkdir(parents=True, exist_ok=True)
cached_paper_ids = [p.stem for p in cached_papers_dir.glob("*.json")]

template_dir = app_dir / "templates"
template_dir.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------- #
@app.command(help="Get a new paper by Arxiv ID, and show it in the terminal")
def get(arxiv_id: Annotated[str, typer.Argument(help="Arxiv ID of a paper")]):
    if arxiv_id in cached_paper_ids:
        print("Fetching from cache...")
        paper = Paper.from_json(cached_papers_dir / f"{arxiv_id}.json")
    else:
        print("Fetching from InspireHEP...")
        inspire = Inspire()
        paper = inspire.get(arxiv_id)

        # If the paper is published, cache it
        if paper.journal != "Unpublished":
            with open(cached_papers_dir / f"{arxiv_id}.json", "w") as f:
                json.dump(paper.__dict__, f, indent=4)
            print(f"Cached in {cached_papers_dir / f'{arxiv_id}.json'}")

    print(
        Panel.fit(
            f"[green]Title[/green]: [bold][{paper.arxiv_id}] {paper.title}[/bold]\n"
            f"[green]Authors[/green]: {', '.join(paper.authors)}\n"
            f"[green]Journal[/green]: {paper.journal}\n"
            f"[green]Citations[/green]: {paper.citations}\n"
            f"[green]Abstract[/green]: {paper.abstract}",
            width=80,
        )
    )


@app.command()
def auth(token: str):
    token_file = app_dir / "auth.yml"
    with open(token_file, "w") as f:
        yaml.dump({"token": token}, f)

    print(f"Token saved in {token_file}")


@app.command(help="Add a new page to a database")
def add(template: str, parameters: str):
    token_file = app_dir / "auth.yml"
    with open(token_file, "r") as f:
        token = yaml.safe_load(f)["token"]

    # Create a Notion client
    client = Client(token)

    # Resolve the template and parameters
    parameters = parameters.split(",")
    template = template_dir / f"{template}.yml"

    # Load the template
    with open(template, "r") as f:
        template = yaml.safe_load(f)

    # Instantiate the engine
    engine = getattr(import_module("hpm.engines"), template["engine"])()

    # Unpack the parameters and pass them to the engine to get the results
    engine_results = engine.get(*parameters)

    # Get the database according to the template
    database_id = template["database"]
    retrieved_json = client.retrieve_database(database_id).json()
    queried_json = client.query_database(database_id).json()
    database = Database.from_dict(retrieved_json, queried_json)

    # Loop over database properties
    # we need to get related database in DatabaseRelation, then extract its pages's title and id to a dictionary.
    # Then when creating a page with this property, we can find its id by its title.
    for name, prop in database.properties.items():
        if type(prop) == DatabaseRelation:
            related_database_id = prop.value
            retrieved_json = client.retrieve_database(related_database_id).json()
            queried_json = client.query_database(related_database_id).json()
            related_database = Database.from_dict(retrieved_json, queried_json)
            database.properties[name] = DatabaseRelation(
                {i.title: i.id for i in related_database.pages}
            )

    # Convert database properties to page properties
    property_database_to_page = {
        DatabaseMultiSelect: MultiSelect,
        DatabaseNumber: Number,
        DatabaseRelation: Relation,
        DatabaseRichText: RichText,
        DatabaseSelect: Select,
        DatabaseTitle: Title,
        DatabaseURL: URL,
    }

    # Use database properties for page properties
    page = Page(
        parent_id=database_id,
        properties={
            name: property_database_to_page[type(property)]()
            for name, property in database.properties.items()
        },
    )

    # Extract property values from engine results according to the template
    for source, target in template["properties"].items():
        property = page.properties[target]
        if type(property) == Relation:
            for i in getattr(engine_results, source):
                if i in database.properties[target].value:
                    page.properties[target].value.append(database.properties[target].value[i])
        else:
            page.properties[target].value = getattr(engine_results, source)

    # Create the page
    response = client.create_page(database_id, page.properties_to_dict())
    if response.status_code == 200:
        print("Page created successfully!")
    else:
        print("Page creation failed!")
        print(response.text)
        raise typer.Exit(code=1)


def version_callback(value: bool):
    if value:
        print(f"{__app_name__} version {__app_version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        Optional[bool],
        typer.Option(
            "-v",
            "--version",
            callback=version_callback,
            is_eager=True,
            help="Show the app version info",
        ),
    ] = None
):
    ...
