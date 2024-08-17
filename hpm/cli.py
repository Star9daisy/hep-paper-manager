from pathlib import Path
from typing import Optional

import pyfiglet
import typer
import yaml
from notion_database.database import Database
from notion_database.page import Page
from notion_database.properties import Properties
from notion_database.search import Direction, Search, Timestamp
from rich.console import Console
from rich.prompt import Prompt
from typing_extensions import Annotated

from . import __app_name__, __app_version__
from .engines import Inspire
from .styles import theme

APP_DIR = Path(typer.get_app_dir("hpm", force_posix=True))
TOKEN_FILE = APP_DIR / "TOKEN"
TEMPLATE_FILE = APP_DIR / "paper.yml"

app = typer.Typer(
    context_settings={"help_option_names": ["-h", "--help"]},
    add_completion=False,
)

c = Console(theme=theme)
print = c.print


@app.command(help="Initialize with the Notion API token")
def init():
    # Welcome info
    print(pyfiglet.figlet_format(f"{__app_name__} {__app_version__}", font="slant"))
    print(
        "Welcome to HEP Paper Manager.\n"
        "It helps add a paper from InspireHEP to Notion database"
    )
    print()

    # Create the app directories
    APP_DIR.mkdir(parents=True, exist_ok=True)

    # Ask for the token
    token = Prompt.ask(
        "[ques]?[/ques] Enter the integration token",
        password=True,
        console=c,
    )
    print()

    # Check if token is valid
    try:
        S = Search(token)
        S.search_database(
            query="",
            sort={
                "direction": Direction.ascending,
                "timestamp": Timestamp.last_edited_time,
            },
        )
    except Exception:
        print("[error]Invalid token!")
        typer.Exit(1)

    # Save the token
    with open(TOKEN_FILE, "w") as f:
        f.write(token)

    # Show the databases to choose from
    for index, database in enumerate(S.result, start=1):
        title = database["title"][0]["plain_text"]
        id = database["id"]
        print(f"[num]{index}[/num]: {title} ({id})")

    # Ask for the database
    choice = Prompt.ask(
        "[ques]?[/ques] Choose one as the paper database",
        default="1",
        console=c,
    )
    print()
    choice = int(choice) - 1
    database_id = S.result[choice]["id"]

    # Modify the provided template file to replace the database_id
    template = Path(__file__).parent / "templates/paper.yml"
    with template.open() as f:
        template_content = yaml.safe_load(f)
        template_content["database_id"] = database_id

    # Save the template file
    with TEMPLATE_FILE.open("w") as f:
        yaml.dump(template_content, f, sort_keys=False)

    print("[done]✔[/done] Initialized!")


@app.command(help="Add a paper via its ArXiv ID")
def add(arxiv_id: str):
    print(f"[sect]>[/sect] Adding paper [num]{arxiv_id}[/num] to the database...")
    print()

    # Load the token
    with open(TOKEN_FILE) as f:
        token = f.read()

    # Load the template
    with open(TEMPLATE_FILE) as f:
        template = yaml.safe_load(f)

    # Get the paper
    print("[info]i[/info] Getting the paper from Inspire")
    paper = Inspire().get(arxiv_id)

    # Check if it exists according to the title
    print("[info]i[/info] Checking if it exists in the database")
    D = Database(token)

    ## Find title column
    D.retrieve_database(database_id=template["database_id"])

    property_dict = {}
    title_column = None
    for property in D.result["properties"].values():
        property_dict[property["name"]] = property["type"]
        if property["type"] == "title":
            title_column = property["name"]

    ## Check if the title exists
    ## The default query only returns 100 results, so we need to loop through all
    D.run_query_database(database_id=template["database_id"])

    all_pages = []
    while True:
        all_pages += D.result["results"]

        if D.result["has_more"]:
            D.find_all_page(
                template["database_id"],
                start_cursor=D.result["next_cursor"],
            )
        else:
            break

    for page in all_pages:
        title = page["properties"][title_column]["title"][0]["plain_text"]
        if title == paper.title:
            print()
            print(
                "[error]Error:[/error] [error_msg]This paper already exists in the database."
            )
            print()
            print(f"[hint]Check it here: [url]{page['url']}")
            raise typer.Exit(1)

    # Convert paper to page and create it in the database
    print("[info]i[/info] Creating the page in the database")

    properties = Properties()
    for paper_property, page_property in template["properties"].items():
        property_type = property_dict[page_property]
        if getattr(paper, paper_property) is not None:
            getattr(properties, f"set_{property_type}")(
                page_property, getattr(paper, paper_property)
            )

    P = Page(integrations_token=token)
    P.create_page(template["database_id"], properties)

    print()
    print("[done]✔[/done] Added")
    print()
    print(f"[hint]Check it here: [url]{P.result['url']}")


@app.command(help="Update a paper or all papers")
def update(arxiv_id: str):
    # Load the token
    with open(TOKEN_FILE) as f:
        token = f.read()

    # Load the template
    with open(TEMPLATE_FILE) as f:
        template = yaml.safe_load(f)

    if arxiv_id != "all":
        print(f"[sect]>[/sect] Updating paper [num]{arxiv_id}[/num]...")
        print()

        # Get the paper
        print("[info]i[/info] Getting the paper from Inspire")
        paper = Inspire().get(arxiv_id)

        # Check if it exists according to the title
        print("[info]i[/info] Checking if it exists in the database")
        D = Database(token)

        ## Find title column
        D.retrieve_database(database_id=template["database_id"])

        property_dict = {}
        title_column = None
        for property in D.result["properties"].values():
            property_dict[property["name"]] = property["type"]
            if property["type"] == "title":
                title_column = property["name"]

        ## Check if the title exists and get the page id
        is_existing = False
        page_id = None
        D.run_query_database(database_id=template["database_id"])

        ## The default query only returns 100 results, so we need to loop through all
        all_pages = []
        while True:
            all_pages += D.result["results"]

            if D.result["has_more"]:
                D.find_all_page(
                    template["database_id"],
                    start_cursor=D.result["next_cursor"],
                )
            else:
                break

        for page in all_pages:
            title = page["properties"][title_column]["title"][0]["plain_text"]
            if title == paper.title:
                is_existing = True
                page_id = page["id"]
                break

        if not is_existing:
            print()
            print(
                "[error]Error:[/error] [error_msg]This paper does not exist in the database."
            )
            raise typer.Exit(1)

        # Convert paper to page and create it in the database
        print("[info]i[/info] Updating the page in the database")

        properties = Properties()
        for paper_property, page_property in template["properties"].items():
            property_type = property_dict[page_property]
            if getattr(paper, paper_property) is not None:
                getattr(properties, f"set_{property_type}")(
                    page_property, getattr(paper, paper_property)
                )

        P = Page(integrations_token=token)
        P.update_page(page_id, properties)

        print()
        print("[done]✔[/done] Updated")
        print()
        print(f"Check it here: [url]{P.result['url']}")

    else:
        print("[sect]>[/sect] Updating all papers...")
        print()

        # Get all arxiv ids and page ids
        print("[info]i[/info] Getting all papers from the database")

        D = Database(token)
        D.retrieve_database(database_id=template["database_id"])

        property_dict = {}
        for property in D.result["properties"].values():
            property_dict[property["name"]] = property["type"]

        D.run_query_database(database_id=template["database_id"])

        ## The default query only returns 100 results
        all_pages = []
        while True:
            all_pages += D.result["results"]

            if D.result["has_more"]:
                D.find_all_page(
                    template["database_id"],
                    start_cursor=D.result["next_cursor"],
                )
            else:
                break

        total = len(all_pages)
        for i, page in enumerate(all_pages):
            arxiv_id = page["properties"]["ArXiv ID"]["rich_text"][0]["plain_text"]
            page_id = page["id"]

            print(
                f"[info]i[/info] Updating [{i+1}/{total}] [num]{arxiv_id}[/num]...",
                end="",
            )

            # Get the paper
            # print("[info]i[/info] Getting the paper from Inspire")
            paper = Inspire().get(arxiv_id)

            # Convert paper to page and create it in the database
            # print("[info]i[/info] Updating the page in the database")

            properties = Properties()
            for paper_property, page_property in template["properties"].items():
                property_type = property_dict[page_property]
                if getattr(paper, paper_property) is not None:
                    getattr(properties, f"set_{property_type}")(
                        page_property, getattr(paper, paper_property)
                    )

            P = Page(integrations_token=token)
            P.update_page(page_id, properties)

            print("[done]✔")

        print()
        print("[done]✔[/done] Updated all papers")


def version_callback(value: bool):
    if value:
        print(
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
    ] = None,
): ...
