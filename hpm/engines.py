from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
from datetime import datetime

import requests


@dataclass
class InspirePaper:
    title: str
    authors: list[str]
    date: str
    journal: str | None
    arxiv_id: str
    doi: str | None
    n_citations: int
    n_references: int
    n_pages: int | None
    abstract: str
    bibtex: str
    url: str


class Inspire:
    def __init__(self) -> None:
        self.endpoint = "https://inspirehep.net/api/arxiv"

    def get(self, arxiv_id: str) -> InspirePaper:
        url = f"{self.endpoint}/{arxiv_id}"
        response = requests.get(url)
        info = response.json(object_pairs_hook=OrderedDict)
        meta = info["metadata"]

        # return meta

        # Title -------------------------------------------------------------- #
        title = meta["titles"][0]["title"]

        # Authors ------------------------------------------------------------ #
        authors = []
        if "collaborations" in meta:
            authors.append(f"{meta['collaborations'][0]['value']} Collaboration")
        else:
            for author in meta["authors"][:10]:
                name = " ".join(author["full_name"].split(", ")[::-1])
                authors.append(name)

        # Date --------------------------------------------------------------- #
        if "preprint_date" in meta and meta["preprint_date"].count("-") == 2:
            date = meta["preprint_date"]
        else:
            date = meta["legacy_creation_date"]

        date = datetime.strptime(date, "%Y-%m-%d")
        date = date.strftime("%Y-%m-%d")

        # Citation count ----------------------------------------------------- #
        n_citations = meta["citation_count"]

        # References count --------------------------------------------------- #
        n_references = len(meta["references"])

        # Pages count -------------------------------------------------------- #
        n_pages = meta.get("number_of_pages")

        # Journal ------------------------------------------------------------ #
        if "publication_info" not in meta:
            journal = None
        else:
            for i in meta["publication_info"]:
                if "pubinfo_freetext" in i:
                    journal = i["pubinfo_freetext"].split(",")[0]

                if "journal_title" in i:
                    journal = i["journal_title"]
                    break

                if "cnum" in i:
                    conf_url = i["conference_record"]["$ref"]
                    conf_response = requests.get(conf_url)
                    conf_meta = conf_response.json()["metadata"]
                    if "acronyms" in conf_meta:
                        journal = conf_meta["acronyms"][0]
                    else:
                        journal = conf_meta["titles"][0]["title"]
                    break

        # DOI
        doi = None
        if "dois" in meta:
            doi = meta["dois"][0]["value"]

        # Abstract ----------------------------------------------------------- #
        abstract = meta["abstracts"][0]["value"]
        if len(abstract) > 2000:
            abstract = abstract[:1997] + "..."

        # Bibtex ------------------------------------------------------------- #
        bibtex_link = info["links"]["bibtex"]
        bibtex_response = requests.get(bibtex_link)
        bibtex = bibtex_response.text[:-1]

        # URL ---------------------------------------------------------------- #
        url = f"https://inspirehep.net/literature/{meta['control_number']}"

        return InspirePaper(
            title=title,
            authors=authors,
            date=date,
            journal=journal,
            arxiv_id=arxiv_id,
            doi=doi,
            n_citations=n_citations,
            n_references=n_references,
            n_pages=n_pages,
            abstract=abstract,
            bibtex=bibtex,
            url=url,
        )
