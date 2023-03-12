import shutil
from pathlib import Path
from time import perf_counter, sleep

import rich
import typer

from .engines.inspire import get_paper_by_arxiv_id
from .engines.semantic import get_paper_by_corpus_id
from .notion.database import query_database
from .notion.page import create_page, update_page
from .notion.types import URL, Number, Relation, RichText, Select, Title
from .papers import InspirePaper, NotionPaper, SemanticPaper
from .utils import find_relation_ids

app = typer.Typer(
    context_settings={"help_option_names": ["-h", "--help"]},
    add_completion=False,
)

from configparser import ConfigParser

app_dir = Path(typer.get_app_dir("hpm"))
app_dir.mkdir(exist_ok=True)
config_file = app_dir / "config.ini"

cp = ConfigParser()


# ---------------------------------------------------------------------------- #
@app.command()
def reset():
    """Reset the hpm"""
    print(f"Resetting...", end="", flush=True)
    if app_dir.exists():
        shutil.rmtree(app_dir)
    print("OK")


@app.command()
def auth(token: str):
    """Set the configuration."""
    auth_section = "auth"
    auth_option = "token"
    if not config_file.exists():
        cp.add_section(auth_section)
        cp.set(auth_section, auth_option, token)
        with open(config_file, "w") as f:
            cp.write(f)
    else:
        cp.read(config_file)
        if not cp.has_section(auth_section):
            cp.add_section(auth_section)
        cp.set(auth_section, auth_option, token)
        with open(config_file, "w") as f:
            cp.write(f)


@app.command()
def config(papers: str, professors: str):
    """Config for the databases"""
    if not config_file.exists():
        print("Please use `auth` to set the token first.")
        raise typer.Exit(1)
    else:
        cp.read(config_file)
        if not cp.has_section("databases"):
            cp.add_section("databases")
        cp.set("databases", "papers", papers)
        cp.set("databases", "professors", professors)
        with open(config_file, "w") as f:
            cp.write(f)


@app.command()
def add(corpus_id: str, update: bool = False, page_id: str = ""):
    if not config_file.exists():
        print("Please use `auth` to set the token first.")
        raise typer.Exit(1)

    cp.read(config_file)
    if not cp.has_section("databases"):
        print("Please use `config` to set the databases first.")
        raise typer.Exit(1)

    token = cp.get("auth", "token")
    papers_db = cp.get("databases", "papers")
    professors_db = cp.get("databases", "professors")

    # First send a request to semantic scholar to get the paper by corpus id.
    print("Requesting Semantic Scholar...", end="", flush=True)
    _start = perf_counter()
    sem_paper = SemanticPaper.from_response(get_paper_by_corpus_id(corpus_id))
    sleep(3)
    _end = perf_counter()
    print(f"OK in {_end-_start:.2f}s")

    # Second send a request to inspire to get the paper by arxiv id.
    # if no arxiv_id is found, then NotionPaper only use Semantic Scholar data.
    if sem_paper.arxiv_id != "":
        print("Requesting Inspire...", end="", flush=True)
        _start = perf_counter()
        ins_paper = InspirePaper.from_response(get_paper_by_arxiv_id(sem_paper.arxiv_id))
        _end = perf_counter()
        print(f"OK in {_end-_start:.2f}s")

        # Transform the authors to relation ids.
        print("Finding authors...", end="", flush=True)
        _start = perf_counter()
        authors = ins_paper.authors
        ids = find_relation_ids(token, professors_db, authors)
        _end = perf_counter()
        print(f"OK in {_end-_start:.2f}s")

        # Then fill the NotionPaper that represents one page in the Papers database.
        # Note: You need to modify the NotionPaper class to fulfill your needs.
        paper = NotionPaper(
            Title=Title(content=sem_paper.title),
            Published=Select(name=ins_paper.published),
            Authors=Relation(ids=ids),
            Citations=Number(number=ins_paper.citations),
            ArxivID=RichText(content=ins_paper.arxiv_id),
            CorpusID=RichText(content=sem_paper.corpus_id),
            SemanticURL=URL(url=sem_paper.url),
            InspireURL=URL(url=ins_paper.url),
            Bibtex=RichText(content=ins_paper.bibtex),
        )

    else:
        print(sem_paper)
        paper = NotionPaper(
            Title=Title(content=sem_paper.title),
            Published=Select(name=sem_paper.published),
            Authors=Relation(ids=[]),
            Citations=Number(number=sem_paper.citations),
            ArxivID=RichText(content=sem_paper.arxiv_id),
            CorpusID=RichText(content=sem_paper.corpus_id),
            SemanticURL=URL(url=sem_paper.url),
            InspireURL=URL(url=None),
            Bibtex=RichText(content=""),
        )

    # Finally, create the page in the Papers database.
    _start = perf_counter()
    if not update:
        print("Adding to Notion...", end="", flush=True)
        response = create_page(
            token,
            {"type": "database_id", "database_id": papers_db},
            paper.to_properties(),
        )
    else:
        print("Updating in Notion...", end="", flush=True)
        response = update_page(
            token,
            page_id,
            paper.to_properties(),
        )
    _end = perf_counter()
    print(f"OK in {_end-_start:.2f}s")

    if response.status_code == 200:
        rich.print(paper)
    else:
        rich.print(response.text)


@app.command()
def add_from_file(input_file: Path):
    with open(input_file, "r") as f:
        for i, line in enumerate(f):
            print(f"Adding paper {i}...", flush=True)
            corpus_id = line.strip()
            add(corpus_id)


@app.command()
def update():
    if not config_file.exists():
        print("Please use `auth` to set the token first.")
        raise typer.Exit(1)

    cp.read(config_file)
    if not cp.has_section("databases"):
        print("Please use `config` to set the databases first.")
        raise typer.Exit(1)

    # First get the corpus ids of all the papers in the database.
    token = cp.get("auth", "token")
    papers_db = cp.get("databases", "papers")
    response = query_database(
        token, papers_db, sorts=[{"property": "ArxivID", "direction": "ascending"}]
    )
    results = response.json()["results"]

    pages = []
    for result in results:
        _id = result["id"]
        _corpus_id = result["properties"]["CorpusID"]["rich_text"][0]["plain_text"]
        pages.append({"id": _id, "corpus_id": _corpus_id})

    # Then call the `add` command to update the database.
    for i, page in enumerate(pages, start=1):
        print(f"Updating paper #{i}({page['corpus_id']})...")
        add(page["corpus_id"], update=True, page_id=page["id"])
