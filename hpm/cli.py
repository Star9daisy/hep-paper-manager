import json
from collections import OrderedDict
from pathlib import Path
from typing import Optional

import requests
import typer
from rich import print
from rich.panel import Panel
from typing_extensions import Annotated

from . import __app_name__, __app_version__

# ---------------------------------------------------------------------------- #
app = typer.Typer(
    context_settings={"help_option_names": ["-h", "--help"]},
    add_completion=False,
)
app_dir = Path(typer.get_app_dir("hpm", force_posix=True))
app_dir.mkdir(parents=True, exist_ok=True)

cached_papers_dir = app_dir / "cached_papers"
cached_papers_dir.mkdir(parents=True, exist_ok=True)
cached_paper_ids = [p.stem for p in cached_papers_dir.glob("*.json")]


# ---------------------------------------------------------------------------- #
@app.command(help="Get a new paper by Arxiv ID, and show it in the terminal")
def get(arxiv_id: Annotated[str, typer.Argument(help="Arxiv ID of a paper")]):
    if arxiv_id in cached_paper_ids:
        print("Fetching from cache...", flush=True, end="")
        try:
            with open(cached_papers_dir / f"{arxiv_id}.json", "r") as f:
                contents = json.load(f)
        except:
            print("[red]x[/red]")
            raise typer.Exit("Error fetching the cached paper")
        print("[green]✓[/green]")

    else:
        print("Fetching from InspireHEP...", flush=True, end="")

        try:
            url = f"https://inspirehep.net/api/arxiv/{arxiv_id}"
            contents = requests.get(url).json(object_pairs_hook=OrderedDict)
        except:
            print("[red]x[/red]")
            raise typer.Exit("Error fetching the paper")
        print("[green]✓[/green]")

        # Cache the paper
        with open(cached_papers_dir / f"{arxiv_id}.json", "w") as f:
            json.dump(contents, f, indent=4)
        print(f"Cached in {cached_papers_dir / f'{arxiv_id}.json'}")

    metadata = contents["metadata"]
    title = metadata["titles"][-1]["title"]

    authors = []
    if "collaborations" in metadata:
        authors.append(f"{metadata['collaborations'][0]['value']} Collaboration")
    else:
        for author in metadata["authors"][:10]:  # Only get first 10 authors
            author_name = " ".join(author["full_name"].split(", ")[::-1])
            authors.append(author_name)

    match metadata["document_type"][0]:
        case "article":
            try:
                journal = metadata["publication_info"][0]["journal_title"]
            except KeyError:
                journal = "Unpublished"
        case "conference paper":
            for i in metadata["publication_info"]:
                if "cnum" in i:
                    conf_url = i["conference_record"]["$ref"]
                    conf_contents = requests.get(conf_url).json()
                    conf_metadata = conf_contents["metadata"]
                    if "acronyms" in conf_metadata:
                        journal = conf_metadata["acronyms"][0]
                    else:
                        journal = conf_metadata["titles"][0]["title"]
                    break

    citations = metadata["citation_count"]
    abstract = metadata["abstracts"][-1]["value"]

    print(
        Panel.fit(
            f"[green]Title[/green]: [bold][{arxiv_id}] {title}[/bold]\n"
            f"[green]Authors[/green]: {', '.join(authors)}\n"
            f"[green]Journal[/green]: {journal}\n"
            f"[green]Citations[/green]: {citations}\n"
            f"[green]Abstract[/green]: {abstract}",
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
