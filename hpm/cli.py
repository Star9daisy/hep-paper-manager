from typing import Optional

import typer
from typing_extensions import Annotated

from . import __app_name__, __app_version__

# ---------------------------------------------------------------------------- #
app = typer.Typer(
    context_settings={"help_option_names": ["-h", "--help"]},
    add_completion=False,
)


def version_callback(value: bool):
    if value:
        print(f"{__app_name__} version {__app_version__}")
        raise typer.Exit()


@app.command()
def main(
    version: Annotated[
        Optional[bool],
        typer.Option("-v", "--version", callback=version_callback, is_eager=True),
    ] = None
):
    ...
