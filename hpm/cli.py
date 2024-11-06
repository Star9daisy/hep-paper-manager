import pyfiglet
import typer
from rich.prompt import Prompt
from typing_extensions import Annotated, Optional

from hpm.services.inspire_hep.client import InspireHEP
from hpm.services.inspire_hep.objects import Paper
from hpm.services.notion.client import Notion
from hpm.services.notion.objects.database import Database
from hpm.services.notion.objects.page import Page
from hpm.services.notion.objects.page_properties import ALL_PAGE_PROPERTIES

from . import __app_name__, __app_version__
from .config import Config
from .utils import console, print

app = typer.Typer(
    context_settings={"help_option_names": ["-h", "--help"]},
    add_completion=False,
    pretty_exceptions_show_locals=False,
)


@app.command(help="Initialize with the Notion API token")
def init():
    config = Config()

    # Print welcome message -------------------------------------------------- #
    print(pyfiglet.figlet_format(f"{__app_name__} {__app_version__}", font="slant"))
    print("Welcome to HEP Paper Manager.")
    print("It helps add a paper from InspireHEP to Notion database")
    print()

    # Check if hpm has already been initialized ------------------------------ #
    if config.is_initialized():
        is_reinitialized = Prompt.ask(
            "[ques]?[/ques] Already been initialized. Overwrite token?",
            default="y",
            console=console,
            choices=["y", "n"],
        )

        if is_reinitialized == "y":
            config.clean()
            config.initialize()
    else:
        config.initialize()
    print()

    # Ask for the token ---------------------------------------------------------- #
    if config.token_file.exists():
        token = config.load_token()
    else:
        token = Prompt.ask(
            "[ques]?[/ques] Enter the integration token",
            password=True,
            console=console,
        )
        config.save_token(token)
        print("[green]✔[/green] Token saved")

    # Search databases ------------------------------------------------------- #
    notion = Notion(token)
    response = notion.search_database()
    n_databases = len(response["results"])

    print(f"[num]{n_databases}[/num] databases found:")
    for index, result in enumerate(response["results"], start=1):
        title = result["title"][0]["plain_text"]
        url = result["url"]
        print(f"  [num]{index}[/num]: {title} -> ([url]{url}[/url])")
    print()

    # Choose one for papers -------------------------------------------------- #
    choice = Prompt.ask(
        "[ques]?[/ques] Choose one as the paper database",
        default="1",
        console=console,
    )

    choice = int(choice) - 1
    database_id = response["results"][choice]["id"]

    # Modify database id in the template
    template = config.load_built_in_template("paper")
    template["database_id"] = database_id
    config.save_template("paper", template)

    # Finally, save other parameters for the Notion client
    params = {"page_size": 100}
    config.save_config_for_notion_client(params)

    print(f"[green]✔[/green] Choose database ({database_id}) for papers")
    print()

    # ------------------------------------------------------------------------ #
    print("[done]✔[/done] Done!")
    print()


@app.command(help="Add a paper via its ArXiv ID")
def add(arxiv_id: str):
    # Config
    config = Config()
    token = config.load_token()
    template = config.load_template("paper")
    database_id = template["database_id"]
    params = config.load_config_for_notion_client()
    page_size = int(params["page_size"])

    # Clients
    inspire_hep = InspireHEP()
    notion = Notion(token)

    print(f"[sect]>[/sect] Adding paper [num]{arxiv_id}[/num] to the database...")
    print()

    # Retrieve the paper from InspireHEP ------------------------------------- #
    print("[info]i[/info] Retrieving paper from InspireHEP")

    response = inspire_hep.get_paper(arxiv_id)
    paper = Paper.from_response(response)

    # Check if it exists according to the title ------------------------------ #
    print("[info]i[/info] Checking if it's already in Notion")

    # Query the database to get all pages
    start_cursor = None
    while True:
        response = notion.query_database(database_id, start_cursor, page_size)
        pages = [Page.from_response(data) for data in response["results"]]
        titles = [page.title for page in pages]

        if paper.title in titles:
            page = pages[titles.index(paper.title)]
            print("[error]✘[/error] ", end="")
            print("[error_msg]Already in the database[/error_msg]")
            print()
            print(f"[hint]Check it here: [url]{page.url}")
            raise typer.Exit(1)

        if response["has_more"]:
            start_cursor = response["next_cursor"]
        else:
            break

    # Create a new page ------------------------------------------------------ #
    # Retreve the database to get the properties
    response = notion.retrieve_database(database_id)
    database = Database.from_response(response)

    # Prepare the page properties according to the template
    properties = {}
    for paper_property, page_property in template["properties"].items():
        if page_property is None:
            continue

        # Get paper property value
        if "." not in paper_property:
            value = getattr(paper, paper_property)
        else:
            first_level_property = paper_property.split(".")[0]
            second_level_property = paper_property.split(".")[1]
            value = [
                getattr(i, second_level_property)
                for i in getattr(paper, first_level_property)
            ]

        # Get the page property class according to the database property type
        database_property_type = database.properties[page_property].type
        page_property_cls = ALL_PAGE_PROPERTIES[database_property_type]

        # Fill the value into the page property
        properties[page_property] = page_property_cls(value)

    # Create a new page in the database -------------------------------------- #
    print("[info]i[/info] Creating a new page in Notion")

    response = notion.create_page(database_id, properties)
    new_page = Page.from_response(response)

    print()

    # ------------------------------------------------------------------------ #
    print("[done]✔[/done] Added")
    print()
    print(f"[hint]Check it here: [url]{new_page.url}")


@app.command(help="Update a paper or all papers")
def update(arxiv_id: str):
    # Config
    config = Config()
    token = config.load_token()
    template = config.load_template("paper")
    database_id = template["database_id"]
    params = config.load_config_for_notion_client()
    page_size = int(params["page_size"])

    # Clients
    inspire_hep = InspireHEP()
    notion = Notion(token)

    if arxiv_id != "all":
        print(f"[sect]>[/sect] Updating paper [num]{arxiv_id}[/num]...")
    else:
        print("[sect]>[/sect] Updating all papers...")
    print()

    # Get the eprint property name from template
    eprint_property_name = template["properties"]["eprint"]

    # Query the database to get the page or all pages
    existed_paper_pages = []
    start_cursor = None
    while True:
        response = notion.query_database(database_id, start_cursor, page_size)
        pages = [Page.from_response(data) for data in response["results"]]
        page_eprints = [page.properties[eprint_property_name].value for page in pages]

        if arxiv_id != "all":
            if arxiv_id in page_eprints:
                page = pages[page_eprints.index(arxiv_id)]
                existed_paper_pages.append(page)
                break
        else:
            existed_paper_pages += pages

        if response["has_more"]:
            start_cursor = response["next_cursor"]
        else:
            break

    # Check if the paper is in the database
    if arxiv_id != "all" and len(existed_paper_pages) == 0:
        print("[error]✘[/error] ", end="")
        print("[error_msg]Not added to the database yet[/error_msg]")
        raise typer.Exit(1)

    # Update the paper ------------------------------------------------------- #
    n_pages = len(existed_paper_pages)
    for i_page, page in enumerate(existed_paper_pages, start=1):
        arxiv_id = page.properties[eprint_property_name].value
        title = page.title
        print("[info]i[/info] ", end="")
        print(f"Paper [num][{i_page}/{n_pages}][/num]: ", end="")
        print(f"[yellow]\[{arxiv_id}][/yellow] {title}", width=100, soft_wrap=True)

        # Retrieve the paper
        response = inspire_hep.get_paper(arxiv_id)
        paper = Paper.from_response(response)

        # Update the page properties according to the template
        need_update = False
        for i_property, (paper_property, page_property) in enumerate(
            template["properties"].items()
        ):
            if page_property is None:
                continue

            # Get paper property value
            if "." not in paper_property:
                value = getattr(paper, paper_property)
            else:
                first_level_property = paper_property.split(".")[0]
                second_level_property = paper_property.split(".")[1]
                value = [
                    getattr(i, second_level_property)
                    for i in getattr(paper, first_level_property)
                ]

            # Update the page property
            if page.properties[page_property].value != value:
                original_value = page.properties[page_property].value
                print(f"  ┗ Updating {page_property}: {original_value} -> {value}")
                page.properties[page_property].value = value
                need_update = True

            # Print a blank line
            if (i_property == len(template["properties"]) - 1) and need_update:
                print()

        if need_update:
            notion.update_page(page.id, page.properties)

    print()

    # ------------------------------------------------------------------------ #
    print("[done]✔[/done] Updated!")


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
