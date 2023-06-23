import shutil
from importlib import import_module
from pathlib import Path
from typing import Optional

import typer
import yaml
from rich import print
from typing_extensions import Annotated

from hpm import APP_DIR, CACHE_DIR, TEMPLATE_DIR
from hpm.notion.client import Client
from hpm.notion.objects import Database, Page
from hpm.notion.properties import *

from . import __app_name__, __app_version__

# ---------------------------------------------------------------------------- #
app = typer.Typer(
    context_settings={"help_option_names": ["-h", "--help"]},
    add_completion=False,
)


@app.command(help="Initialize hpm with the Notion API token")
def init():
    print("Welcome to the HEP Paper Manager!\n")
    print("Before we start, let's set up a few necessary configurations.\n")
    token = typer.prompt("Enter your Notion API token", hide_input=True)
    token_file = APP_DIR / "auth.yml"
    with open(token_file, "w") as f:
        yaml.dump({"token": token}, f)
    print(f"[green]Your token has been saved in {token_file}\n")

    use_template = typer.confirm("Would you like to use the default paper template?", default=True)
    if use_template:
        paper_template = Path(__file__).parent / "templates/paper.yml"
        shutil.copy(paper_template, TEMPLATE_DIR)
        print(f"[green]The default template has been saved in {TEMPLATE_DIR}/paper.yml")
        print("[yellow]Remember to add a database id to the template before using hpm!\n")

    print("Configuration complete! Here are directories that hpm will use:")
    print(f"1. App directory: {APP_DIR}")
    print(f"2. Template directory: {TEMPLATE_DIR}")
    print(f"3. Cache directory: {CACHE_DIR}")


@app.command(help="Add a new page to a database")
def add(template: str, parameters: str):
    token_file = APP_DIR / "auth.yml"
    with open(token_file, "r") as f:
        token = yaml.safe_load(f)["token"]

    # Create a Notion client
    client = Client(token)

    # Resolve the template and parameters
    parameters = parameters.split(",")
    template = TEMPLATE_DIR / f"{template}.yml"

    # Load the template
    with open(template, "r") as f:
        template = yaml.safe_load(f)

    print(f"-> Launching {template['engine']}")
    # Instantiate the engine
    engine = getattr(import_module("hpm.engines"), template["engine"])()

    # Unpack the parameters and pass them to the engine to get the results
    engine_results = engine.get(*parameters)

    print(f"-> Fetching database {template['database']}")
    # Get the database according to the template
    database_id = template["database"]
    retrieved_json = client.retrieve_database(database_id).json()
    queried_json = client.query_database(database_id).json()
    database = Database.from_dict(retrieved_json, queried_json)

    print(f"-> Creating page in database {database.title}")
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

    # Use template properties for page properties rather than database properties
    # to allow for other properties that are not in the template but in the database
    page = Page(
        parent_id=database_id,
        properties={
            name: property_database_to_page[type(database.properties[name])]()
            for _, name in template["properties"].items()
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
        print(f"{__app_name__} v[yellow]{__app_version__}[/yellow]")
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
