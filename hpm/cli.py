import shutil
from importlib import import_module
from pathlib import Path
from typing import Optional

import typer
import yaml
from notion_database.const.query import Direction, Timestamp
from notion_database.search import Search
from rich.console import Console
from rich.prompt import Confirm, Prompt
from tabulate import tabulate
from typing_extensions import Annotated

from hpm.notion.client import Client
from hpm.notion.objects import Database, Page
from hpm.notion.properties import *

from . import __app_name__, __app_version__
from .styles import theme

# ---------------------------------------------------------------------------- #
APP_DIR = Path(typer.get_app_dir(__app_name__, force_posix=True))
TEMPLATE_DIR = APP_DIR / "templates"
CACHE_DIR = APP_DIR / "cache"

# ---------------------------------------------------------------------------- #
app = typer.Typer(
    context_settings={"help_option_names": ["-h", "--help"]},
    add_completion=False,
)
c = Console(theme=theme)


# ---------------------------------------------------------------------------- #
@app.command(help="Initialize hpm with the Notion API token")
def init():
    # Welcome info ----------------------------------------------------------- #
    c.print(
        "Welcome to HEP Paper Manager.\n"
        "It helps add a paper from InspireHEP to Notion database"
    )

    # Setup app directory ---------------------------------------------------- #
    c.print("\n[sect]>[/sect] Setting up app directory...", end="")
    if APP_DIR.exists():
        c.print("[error]✘")
        c.print("[error]This directory already exists.")
        c.print()
        c.print(
            "[hint]Check out the directory and ensure it could be safely removed.\n"
            f"Use `rmdir {APP_DIR}` or `rm -rf {APP_DIR}` (caution!) to remove it.\n"
            "Then run `hpm init` again."
        )
        raise typer.Exit(1)

    APP_DIR.mkdir()
    TEMPLATE_DIR.mkdir()
    CACHE_DIR.mkdir()
    c.print("[done]✔")

    # Token ------------------------------------------------------------------ #
    token = Prompt.ask(
        "\n[ques]? Enter the integration token",
        console=c,
        password=True,
    )
    if token != "":
        c.print("[done]Integration token added")
    else:
        c.print("[error]Empty integration token")
        c.print()
        c.print(
            "[hint]Integration token is started with 'secret_', "
            "copy and paste it here."
        )
        raise typer.Exit(1)

    with open(APP_DIR / "auth.yml", "w") as f:
        yaml.dump({"token": token}, f)

    # Database --------------------------------------------------------------- #
    c.print("\n[sect]>[/sect] Retriving databases...", end="")
    try:
        S = Search(token)
        S.search_database(
            query="",
            sort={
                "direction": Direction.ascending,
                "timestamp": Timestamp.last_edited_time,
            },
        )
    except:
        c.print("[error]✘")
        c.print("[error]Invalid integration token.")
        c.print()
        c.print(
            "[hint]Please create an integration first. "
            "For more information, check out\n"
            "https://developers.notion.com/docs/create-a-notion-integration"
            "#create-your-integration-in-notion"
        )
        raise typer.Exit(1)
    c.print("[done]✔")

    if len(S.result) == 0:
        c.print("[error]No databases connected to the integration.")
        c.print()
        c.print(
            "[hint]Please add the integration to a database first. "
            "For more information, check out\n"
            "https://developers.notion.com/docs/create-a-notion-integration"
            "#give-your-integration-page-permissions"
        )
        raise typer.Exit(1)

    db_table = {
        "Index": [i for i in range(len(S.result))],
        "Name": [i["title"][0]["plain_text"] for i in S.result],
        "Database ID": [i["id"] for i in S.result],
    }
    c.print(tabulate(db_table, headers="keys", showindex=True))

    db_index = int(
        Prompt.ask("[ques]? Choose one as paper database", console=c, default=0)
    )
    database_id = S.result[db_index]["id"]
    database_name = S.result[db_index]["title"][0]["plain_text"]

    # Template --------------------------------------------------------------- #
    c.print(f"\n[sect]>[/sect] Creating template for {database_name}...", end="")
    paper_template = Path(__file__).parent / "templates/paper.yml"
    with open(paper_template, "r") as f:
        template_content = yaml.safe_load(f)
        template_content["database_id"] = database_id
    try:
        with open(TEMPLATE_DIR / "paper.yml", "w") as f:
            yaml.dump(template_content, f, sort_keys=False)
    except:
        c.print("[error]✘")
        c.print("[error]Failed to create the paper template.")
        c.print()
        c.print(
            f"[hint] Check out the directory {TEMPLATE_DIR} and ensure it exists.\n"
            "Or run `hpm init` again."
        )
        raise typer.Exit(1)
    c.print("[done]✔")
    c.print(f"[done]Paper template saved in {TEMPLATE_DIR / 'paper.yml'}")
    c.print()
    c.print("[hint]Remember to review the template and update it if necessary.")


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
        template_content = yaml.safe_load(f)

    # Check if the database_id is specified in the template
    if (database_id := template_content["database"]) == "<database_id>":
        console.print(
            f"[error]x[/error] Please specify a database id in [path]{template_path}[/path]"
        )
        raise typer.Exit(1)

    console.print(f"[sect]>[/sect] Launching {template_content['engine']} engine")
    # Instantiate the engine
    engine = getattr(import_module("hpm.engines"), template_content["engine"])()

    # Unpack the parameters and pass them to the engine to get the results
    engine_results = engine.get(*parameter_list)
    console.print(f"[done]✔[/done] Engine launched\n")

    console.print(
        f"[sect]>[/sect] Fetching Notion database {template_content['database']}"
    )
    # Get the database according to the template
    database_id = template_content["database"]
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
            for _, name in template_content["properties"].items()
        },
    )

    # Extract property values from engine results according to the template
    for source, target in template_content["properties"].items():
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
