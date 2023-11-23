from pathlib import Path
from typing import Optional

import typer
import yaml
from notion_database.const.query import Direction, Timestamp
from notion_database.database import Database
from notion_database.page import Page
from notion_database.properties import Properties
from notion_database.search import Search
from rich.console import Console
from rich.prompt import Prompt
from tabulate import tabulate
from typing_extensions import Annotated

from . import __app_name__, __app_version__
from .engines import Inspire, InspirePaper
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
    c.print(tabulate(db_table, headers="keys"))

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


@app.command(help="Add an Inpsire paper to a Notion database")
def add(paper_id: str, id_type: str = "literature"):
    # Get the token ---------------------------------------------------------- #
    with open(APP_DIR / "auth.yml", "r") as f:
        token = yaml.safe_load(f).get("token")

    if token is None:
        c.print("[error]No integration token found.")
        c.print()
        c.print("[hint]Please run `hpm init` to initialize the app first.")
        raise typer.Exit(1)

    # Get the template ------------------------------------------------------- #
    with open(TEMPLATE_DIR / "paper.yml", "r") as f:
        template = yaml.safe_load(f)

    # Get the database ------------------------------------------------------- #
    c.print(f"[sect]>[/sect] Retrieving database {template['database_id']}...", end="")
    database_id = template["database_id"]
    D = Database(token)

    try:
        D.retrieve_database(database_id)
    except Exception as e:
        c.print("[error]✘")
        c.print(f"[error]Failed to retrieve the database: {e}")
        raise typer.Exit(1)
    c.print("[done]✔")

    # Get the paper ---------------------------------------------------------- #
    c.print(f"[sect]>[/sect] Retrieving paper {paper_id}...", end="")
    try:
        response_json = Inspire().get(
            identifier_type=id_type,
            identifier_value=paper_id,
        )
    except Exception as e:
        c.print("[error]✘")
        c.print(f"[error]Failed to retrieve the paper: {e}")
        raise typer.Exit(1)
    c.print(f"[done]✔")
    paper = InspirePaper.from_dict(response_json)

    # Paper -> Page according to the template -------------------------------- #
    properties = Properties()
    for prop, database_col in template["properties"].items():
        col_type = D.result["properties"][database_col]["type"]
        getattr(properties, f"set_{col_type}")(database_col, getattr(paper, prop))

    # Create the page -------------------------------------------------------- #
    c.print(f"[sect]>[/sect] Creating page for {paper.title}...", end="")
    page = Page(token)

    try:
        page.create_page(database_id, properties)
    except Exception as e:
        c.print("[error]✘")
        c.print(f"[error]Failed to create the page: {e}")
        raise typer.Exit(1)
    c.print("[done]✔")


@app.command()
def info():
    if not APP_DIR.exists():
        c.print("[error]No app directory found.")
        c.print()
        c.print("[hint]Please run `hpm init` to initialize the app first.")
        raise typer.Exit(1)

    c.print(f"[sect]>[/sect] App directory:")
    c.print(f"[path]{APP_DIR}\n")

    c.print(f"[sect]>[/sect] Auth file:")
    c.print(f"[path]{APP_DIR / 'auth.yml'}\n")

    c.print(f"[sect]>[/sect] Template file:")
    c.print(f"[path]{TEMPLATE_DIR / 'paper.yml'}\n")

    with (TEMPLATE_DIR / "paper.yml").open() as f:
        template = yaml.safe_load(f)

    properties = {"Paper": [], "Database": []}
    for prop, database_col in template["properties"].items():
        properties["Paper"].append(prop)
        properties["Database"].append(database_col)

    c.print(f"[sect]>[/sect] Database ID:")
    c.print(f"[number]{template['database_id']}\n")
    c.print(f"[sect]>[/sect] Paper template properties:")
    c.print(tabulate(properties, headers="keys"))


def version_callback(value: bool):
    if value:
        c.print(
            "== [bold]HEP Paper Manager[/bold] ==\n"
            f"{__app_name__} @v[bold cyan]{__app_version__}[/bold cyan]\n\n"
            "Made by Star9daisy with [bold red]♥[/bold red]"
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
