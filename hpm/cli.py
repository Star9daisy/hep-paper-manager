from rich import print
from importlib import import_module
from hpm.notion import Client
from hpm.notion.objects import Page
from pathlib import Path
from hpm.tools import get_database
from configparser import ConfigParser
import typer
from typing import Optional

app = typer.Typer(
    context_settings={"help_option_names": ["-h", "--help"]},
    add_completion=False,
)

app_dir = Path(typer.get_app_dir("hpm", force_posix=True))
if not app_dir.exists():
    app_dir.mkdir()


cp = ConfigParser()
config_file = app_dir / "config.ini"
if not config_file.exists():
    config_file.touch()
cp.read(config_file)
if "auth" not in cp.sections():
    cp.add_section("auth")
if "default" not in cp.sections():
    cp.add_section("default")
if "databases" not in cp.sections():
    cp.add_section("databases")


@app.command()
def config(
    key: str = typer.Argument(..., help="Config name in [token, database, plugin]"),
    value: str = typer.Argument(..., help="Config value"),
):
    """
    Set the configuration of hpm
    """
    if key == "token":
        print(f"Add token: {value}")
        cp["auth"]["token"] = value
    elif key == "database":
        print(f"Set default database: {value}")
        cp["default"]["database"] = value
    elif key == "plugin":
        print(f"Set default plugin: {value}")
        cp["default"]["plugin"] = value
    else:
        print(f"[red]Need to specify the configuration key and value.")
        print(f"[red]available keys: token, database, plugin")
        raise typer.Exit(1)

    with open(config_file, "w") as f:
        cp.write(f)


@app.command()
def link(
    database_id: str = typer.Argument(..., help="Notion database id"),
    relink: bool = typer.Option(
        False, "--relink", help="If set, will relink to the newest version"
    ),
):
    """
    Link to Notion database

    This command will cache the database and pages locally. Add `--relink` to relink to the newest version.
    """
    if "token" not in cp["auth"]:
        print("[red]No token found. Please run `hpm config token <your-token>` first.")
        raise typer.Exit(1)

    database = get_database(
        cp["auth"]["token"],
        database_id,
        relink=relink,
        verbose=1,
    )

    cp["databases"][database.title] = database_id
    with open(config_file, "w") as f:
        cp.write(f)


@app.command()
def add(
    parameter: str,
    plugin: Optional[str] = typer.Option(None, "--plugin"),
    database_id: Optional[str] = typer.Option(None, "--database-id"),
):
    """
    Add one paper by the plguin and the parameter to Notion database

    This command will use the default plugin and database if not specified.
    """
    if "token" not in cp["auth"]:
        print("[red]No token found. Please run `hpm config token <your-token>` first.")
        raise typer.Exit(1)
    else:
        token = cp["auth"]["token"]

    if "database" not in cp["default"] and not database_id:
        print(
            f"[red]Please specify a database by its id"
            f" or use `hpm config default <database-name>` to set one."
        )
        raise typer.Exit(1)
    if "plugin" not in cp["default"] and not plugin:
        print(
            f"[red]Please specify a plugin by its name"
            f" or use `hpm config default <plugin-name>` to set one."
        )
        raise typer.Exit(1)
    else:
        database_name = cp["default"]["database"]
        database_id = cp["databases"][database_name]
        plugin = cp["default"]["plugin"]

    module = import_module(f"hpm.plugins.{plugin}")
    page = module.main(token, database_id, parameter)

    print(f"Adding page to Notion ({database_id})...", end="", flush=True)
    nc = Client(token)
    response = nc.create_a_page(page, database_id)

    if response.status_code != 200:
        print()
        raise Exception(response.text)
    else:
        print("OK")
        new_page = Page.from_json(response.json())
        print(f"\nCheck it out here:\n{new_page.url}")


@app.command()
def show():
    """
    Show the current configuration
    """
    print(f"Configuration file: {config_file}")
    print("[blue]Auth token:")
    print(f"[white]{cp['auth'].get('token')}")

    print("\n[blue]Currently linked databases:")
    for db_name, db_id in cp["databases"].items():
        print(f"{db_name}: [white]{db_id}")

    print("\n[blue]Currently available plugins:")
    print("inspire_paper: Fetch paper information from InspireHEP")
    print(
        "semantic_and_inspire_paper: Fetch paper information from Semantic Scholar and InspireHEP"
    )

    print("\n[blue]Default:")
    for k, v in cp["default"].items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    app()
