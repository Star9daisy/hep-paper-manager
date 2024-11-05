import shutil
from pathlib import Path

import pyfiglet
import typer
import yaml
from rich.prompt import Prompt
from typing_extensions import Annotated, Optional

from hpm.services.inspire_hep.client import InspireHEP
from hpm.services.inspire_hep.objects import Author, Paper
from hpm.services.notion.client import Notion
from hpm.services.notion.objects.page import Page
from hpm.services.notion.objects.page_properties import ALL_PAGE_PROPERTIES

from . import __app_name__, __app_version__
from .config import APP_DIR, TEMPLATE_FILE, TOKEN_FILE
from .utils import c, print

app = typer.Typer(
    context_settings={"help_option_names": ["-h", "--help"]},
    add_completion=False,
    pretty_exceptions_show_locals=False,
)


@app.command(help="Initialize with the Notion API token")
def init():
    # Welcome info ----------------------------------------------------------- #
    print(pyfiglet.figlet_format(f"{__app_name__} {__app_version__}", font="slant"))
    print(
        "Welcome to HEP Paper Manager.\n"
        "It helps add a paper from InspireHEP to Notion database"
    )
    print()

    # Check if hpm has already been initialized ------------------------------ #
    reinitialized = False
    if APP_DIR.exists():
        if (
            Prompt.ask(
                "[ques]?[/ques] hpm has already been initialized. Clean and reinitialize?",
                default="y",
                console=c,
                choices=["y", "n"],
            )
            == "y"
        ):
            reinitialized = True
            shutil.rmtree(APP_DIR)
            APP_DIR.mkdir()
    else:
        reinitialized = True
        APP_DIR.mkdir()
    print()

    # Ask for the token ------------------------------------------------------ #
    if reinitialized:
        token = Prompt.ask(
            "[ques]?[/ques] Enter the integration token",
            password=True,
            console=c,
        )
        print()

        with open(TOKEN_FILE, "w") as f:
            f.write(token)
        print("[green]✔[/green] Token saved")
        print()
    else:
        with open(TOKEN_FILE, "r") as f:
            token = f.read()

    # Choose the database ---------------------------------------------------- #
    # Search all databases related to the token
    notion = Notion(token)
    response = notion.search_database()
    n_databases = len(response["results"])
    print(f"[num]{n_databases}[/num] databases found:")
    for index, result in enumerate(response["results"], start=1):
        title = result["title"][0]["plain_text"]
        url = result["url"]
        print(f"  [num]{index}[/num]: {title} -> ([url]{url}[/url])")
    print()

    choice = Prompt.ask(
        "[ques]?[/ques] Choose one as the paper database",
        default="1",
        console=c,
    )
    print()
    choice = int(choice) - 1
    database_id = response["results"][choice]["id"]
    print(f"[green]✔[/green] Database ID: {database_id}")
    print()

    # Modify the provided template file to replace the database_id ----------- #
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

    # Get the paper ---------------------------------------------------------- #
    print("[info]i[/info] Getting the paper from Inspire")
    paper_response = InspireHEP().get_paper(arxiv_id)
    paper = Paper.from_response(paper_response)

    # Check if it exists according to the title
    print("[info]i[/info] Checking if it exists in the database")
    database_id = template["database_id"]
    notion = Notion(token)

    retrieved_database_data = notion.retrieve_database(database_id)
    title_property = [
        property["name"]
        for property in retrieved_database_data["properties"].values()
        if property["type"] == "title"
    ][0]

    all_page_data = []
    has_more = True
    while has_more:
        response = notion.query_database(database_id)
        all_page_data += response["results"]
        has_more = response["has_more"]

    for page_data in all_page_data:
        if (
            page_data["properties"][title_property]["title"][0]["plain_text"]
            == paper.title
        ):
            print(f"Paper [{paper.eprint}]{paper.title} already exists")
            raise typer.Exit(1)

    # Create template page according to the database ------------------------- #
    template_page = Page(
        properties={
            k: ALL_PAGE_PROPERTIES[v["type"]]()
            for k, v in retrieved_database_data["properties"].items()
            if v["type"] in ALL_PAGE_PROPERTIES
        }
    )

    # Update the template page according to the paper ------------------------ #
    for paper_property, page_property in template["properties"].items():
        if page_property is None:
            continue

        if "." not in paper_property:
            value = getattr(paper, paper_property)
        else:
            first_level_property = paper_property.split(".")[0]
            second_level_property = paper_property.split(".")[1]
            value = [
                getattr(i, second_level_property)
                for i in getattr(paper, first_level_property)
            ]

        template_page.properties[page_property].value = value

    # Create a new page
    response = notion.create_page(database_id, template_page.properties)
    new_page = Page.from_response(response)
    print()
    print("[done]✔[/done] Paper added")
    print()
    print(f"[hint]Check it here: [url]{new_page.url}[/url]")


@app.command(help="Update a paper or all papers")
def update(arxiv_id: str):
    # Load the token
    with open(TOKEN_FILE) as f:
        token = f.read()

    # Load the template
    with open(TEMPLATE_FILE) as f:
        template = yaml.safe_load(f)
    database_id = template["database_id"]

    # Setup clients
    inspire_hep = InspireHEP()
    notion = Notion(token)

    if arxiv_id != "all":
        print(f"[sect]>[/sect] Updating paper [num]{arxiv_id}[/num]")
        print()

        # Get the paper
        print("[info]i[/info] Getting the paper from Inspire")
        paper_response = inspire_hep.get_paper(arxiv_id)
        paper = Paper.from_response(paper_response)

        # Check if it exists according to the title
        print("[info]i[/info] Checking if it exists in the database")

        retrieved_database_data = notion.retrieve_database(database_id)
        title_property = [
            property["name"]
            for property in retrieved_database_data["properties"].values()
            if property["type"] == "title"
        ][0]

        exists = False
        template_page = Page()
        all_page_data = []
        has_more = True
        start_cursor = None
        while has_more:
            response = notion.query_database(database_id, start_cursor=start_cursor)
            all_page_data += response["results"]
            has_more = response["has_more"]
            start_cursor = response["next_cursor"]

        for page_data in all_page_data:
            if (
                page_data["properties"][title_property]["title"][0]["plain_text"]
                == paper.title
            ):
                template_page = Page.from_response(page_data)
                exists = True
                break

        if not exists:
            print(
                f"Paper [{paper.eprint}]{paper.title} hasn't been added to this database yet"
            )
            raise typer.Exit(1)

        # Update the template page according to the paper -------------------- #
        need_update = False
        for i_property, (paper_property, page_property) in enumerate(
            template["properties"].items()
        ):
            if page_property is None:
                continue

            if "." not in paper_property:
                value = getattr(paper, paper_property)
            else:
                first_level_property = paper_property.split(".")[0]
                second_level_property = paper_property.split(".")[1]
                value = [
                    getattr(i, second_level_property)
                    for i in getattr(paper, first_level_property)
                ]

            if template_page.properties[page_property].value != value:
                original_value = template_page.properties[page_property].value
                print(f"  └ Updating {page_property}: {original_value} -> {value}")
                template_page.properties[page_property].value = value
                need_update = True

            if (i_property == len(template["properties"]) - 1) and need_update:
                print()

        if need_update:
            updated_page = notion.update_page(
                template_page.id, template_page.properties
            )
            print()

        print("[done]✔[/done] Paper updated")
        print()
        print(f"[hint]Check it here: [url]{updated_page['url']}[/url]")

    else:
        print("[sect]>[/sect] Updating all papers in the database")
        print()

        all_page_data = []
        has_more = True
        start_cursor = None
        while has_more:
            response = notion.query_database(database_id, start_cursor=start_cursor)
            all_page_data += response["results"]
            has_more = response["has_more"]
            start_cursor = response["next_cursor"]

        for i_page, page_data in enumerate(all_page_data, start=1):
            template_page = Page.from_response(page_data)
            arxiv_id_col_name = template["properties"]["eprint"]
            title_col_name = template["properties"]["title"]
            arxiv_id = template_page.properties[arxiv_id_col_name].value
            title = template_page.properties[title_col_name].value
            print(
                f"[info]i[/info] Paper [{i_page}/{len(all_page_data)}]: {arxiv_id} : {title}"
            )

            paper_response = inspire_hep.get_paper(arxiv_id)
            paper = Paper.from_response(paper_response)

            need_update = False
            for i_property, (paper_property, page_property) in enumerate(
                template["properties"].items()
            ):
                if page_property is None:
                    continue

                if "." not in paper_property:
                    value = getattr(paper, paper_property)
                else:
                    first_level_property = paper_property.split(".")[0]
                    second_level_property = paper_property.split(".")[1]
                    value = [
                        getattr(i, second_level_property)
                        for i in getattr(paper, first_level_property)
                    ]

                if template_page.properties[page_property].value != value:
                    original_value = template_page.properties[page_property].value
                    print(f"  └ {page_property}: {original_value} -> {value}")
                    template_page.properties[page_property].value = value
                    need_update = True

                if (i_property == len(template["properties"]) - 1) and need_update:
                    print()

            if need_update:
                notion.update_page(template_page.id, template_page.properties)

        print()
        print("[done]✔[/done] All papers updated")


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
