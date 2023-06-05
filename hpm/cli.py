import json
from pathlib import Path
from typing import Optional

import typer
from rich import print
from rich.panel import Panel
from typing_extensions import Annotated
from hpm import CACHED_PAPERS_DIR
from hpm.engines.inspire import Inspire, Paper

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
