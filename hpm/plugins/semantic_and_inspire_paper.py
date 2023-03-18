from __future__ import annotations

from hpm.engines import InspireEngine, SemanticEngine
from hpm.notion.objects import Page
from hpm.notion.properties import URL, Number, Relation, RichText, Select, Title
from hpm.tools import get_database


# ---------------------------------------------------------------------------- #
def main(token: str, database_id: str, corpus_id: str):
    # Get the papers database
    print("Fetching database...", end="", flush=True)
    papers = get_database(token, database_id)
    print("OK")

    # Retrieve the paper from the Semantic Engine
    print("Fetching paper from Semantic...", end="", flush=True)
    se = SemanticEngine()
    sem_paper = se.retrieve_a_paper(corpus_id)
    print("OK")

    if sem_paper.arxiv_id != "":
        # Retrieve the paper from the Inspire Engine
        print("Fetching paper from Inspire...", end="", flush=True)
        ie = InspireEngine()
        ins_paper = ie.retrieve_a_paper(sem_paper.arxiv_id)
        print("OK")

        print("Fetching authors' id...", end="", flush=True)
        ids = []
        related_db = get_database(token, papers.get_property("Authors").value)
        for author in ins_paper.authors:
            for page in related_db.pages:
                if page.title == author:
                    ids.append(page.id)
        print("OK")

        page = Page(
            properties=[
                RichText("ArxivID", ins_paper.arxiv_id),
                RichText("CorpusID", sem_paper.corpus_id),
                Title("Title", ins_paper.title),
                Relation("Authors", ids),
                Select("Published", ins_paper.published),
                Number("Citations", ins_paper.citations),
                URL("SemanticURL", sem_paper.url),
                URL("InspireURL", ins_paper.url),
                RichText("Bibtex", ins_paper.bibtex),
            ]
        )

    else:
        print("Fetching authors' id...", end="", flush=True)
        ids = []
        related_db = get_database(token, papers.get_property("Authors").value)
        for author in sem_paper.authors:
            for page in related_db.pages:
                if page.title == author:
                    ids.append(page.id)
        print("OK")

        page = Page(
            properties=[
                RichText("CorpusID", sem_paper.corpus_id),
                Title("Title", sem_paper.title),
                Relation("Authors", ids),
                Select("Published", sem_paper.published),
                Number("Citations", sem_paper.citations),
                URL("SemanticURL", sem_paper.url),
            ]
        )

    return page
