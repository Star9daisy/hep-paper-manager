import shutil
from importlib import import_module
from pathlib import Path
from typing import Optional

import typer
import yaml
from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.theme import Theme
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

console = Console(
    theme=Theme(
        {
            "sect": "bold white",  # section
            "info": "bold blue",  # informatiom
            "done": "bold green",  # done
            "ques": "bold yellow",  # question
            "error": "bold red",  # error
            "warn": "yellow",  # warning
            "path": "cyan underline",  # path
            "number": "cyan",  # number
        },
        inherit=False,
    )
)


@app.command(help="Initialize hpm with the Notion API token")
def init():
    console.print("Welcome to the HEP Paper Manager!\n")
    console.print("Before we start, let's set up a few necessary configurations.\n")
    token = Prompt.ask(
        "[ques]?[/ques] Enter your Notion API token", console=console, password=True
    )
    token_file = APP_DIR / "auth.yml"
    with open(token_file, "w") as f:
        yaml.dump({"token": token}, f)
    console.print(f"[done]✔[/done] Your token has been saved in {token_file}\n")

    use_template = Confirm.ask(
        "[ques]?[/ques] Would you like to use the default paper template?",
        console=console,
        default=True,
    )
    if use_template:
        paper_template = Path(__file__).parent / "templates/paper.yml"
        shutil.copy(paper_template, TEMPLATE_DIR)
        console.print(
            f"[done]✔[/done] The default template has been saved in {TEMPLATE_DIR}/paper.yml"
        )
        console.print(
            "[warn]Remember to add a database id to the template before using hpm!\n"
        )

    console.print("Configuration complete! Here are directories that hpm will use:")
    console.print(f"1. App directory: {APP_DIR}")
    console.print(f"2. Template directory: {TEMPLATE_DIR}")
    console.print(f"3. Cache directory: {CACHE_DIR}")


@app.command(help="Add a new page to a database")
def add(template: str, parameters: str):
    token_file = APP_DIR / "auth.yml"
    with open(token_file, "r") as f:
        token = yaml.safe_load(f)["token"]

    # Create a Notion client
    client = Client(token)

    # Resolve the template and parameters
    parameter_list = parameters.split(",")
    template_path = TEMPLATE_DIR / f"{template}.yml"

    # Load the template
    with open(template_path, "r") as f:
        template = yaml.safe_load(f)

    # Check if the database_id is specified in the template
    database_id = template["database"]
    if database_id == "<database_id>":
        console.print(
            f"[error]x[/error] Please specify a database id in [path]{template_path}[/path]"
        )
        raise typer.Exit(1)

    console.print(f"[sect]>[/sect] Launching {template['engine']} engine")
    # Instantiate the engine
    engine = getattr(import_module("hpm.engines"), template["engine"])()

    # Unpack the parameters and pass them to the engine to get the results
    engine_results = engine.get(*parameter_list)
    console.print(f"[done]✔[/done] Engine launched\n")

    console.print(f"[sect]>[/sect] Fetching Notion database {template['database']}")
    # Get the database according to the template
    database_id = template["database"]
    retrieved_json = client.retrieve_database(database_id).json()
    queried_json = client.query_database(database_id).json()
    database = Database.from_dict(retrieved_json, queried_json)
    console.print(f"[done]✔[/done] Database fetched\n")

    console.print(f"[sect]>[/sect] Creating page in database {database.title}")
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
                    page.properties[target].value.append(
                        database.properties[target].value[i]
                    )
        else:
            if type(property) == Title:
                page.title = getattr(engine_results, source)
            page.properties[target].value = getattr(engine_results, source)

    # Check if the page already exists
    for i in database.pages:
        if i.title == page.title:
            console.print("[error]![/error] Page already exists!")
            raise typer.Exit(code=1)

    # Create the page
    response = client.create_page(database_id, page.properties_to_dict())
    if response.status_code == 200:
        console.print("[done]✔️[/done] Page created successfully!")
    else:
        console.print("[error]x[/error] Page creation failed!")
        print(response.text)
        raise typer.Exit(code=1)


def version_callback(value: bool):
    if value:
        console.print(
            f"[bold]{__app_name__}[/bold] (version [number]{__app_version__}[/number])"
        )
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
