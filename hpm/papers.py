from __future__ import annotations
import json
from dataclasses import dataclass, field

import requests

from .notion.types import URL, Number, Relation, RichText, Select, Title


# ---------------------------------------------------------------------------- #
@dataclass
class SemanticPaper:
    title: str = ""
    authors: list[str] = field(default_factory=list)
    published: str = "Unpublished"
    citations: int = 0
    corpus_id: str = ""
    arxiv_id: str = ""
    url: str = ""

    @classmethod
    def from_response(cls, response):
        meta = json.loads(response.text)

        cls = SemanticPaper()
        cls.title = meta["title"]
        cls.authors = [a["name"].replace(" ", "") for a in meta["authors"][:10]]
        cls.published = meta["journal"]["name"] if meta["journal"] else "Unpublished"
        if cls.published == "":
            cls.published = "Unpublished"
        cls.citations = meta["citationCount"]
        cls.corpus_id = str(meta["externalIds"].get("CorpusId", ""))
        cls.arxiv_id = meta["externalIds"].get("ArXiv", "")
        cls.url = meta["url"]

        return cls


@dataclass
class InspirePaper:
    title: str = ""
    authors: list[str] = field(default_factory=list)
    published: str = "Unpublished"
    citations: int = 0
    arxiv_id: str = ""
    url: str = ""
    bibtex: str = ""

    @classmethod
    def from_response(cls, response):
        contents = json.loads(response.text)
        bibtex_link = contents["links"]["bibtex"]
        meta = contents["metadata"]

        cls = InspirePaper()

        # title
        cls.title = meta["titles"][0]["title"]

        # authors
        if "collaborations" in meta:
            cls.authors = [f"{meta['collaborations'][0]['value']} Collaborations"]
        else:
            for author in meta["authors"][:10]:
                if "ids" not in author:
                    author_link = author["record"]["$ref"]
                    author_response = requests.get(author_link)
                    author_contents = json.loads(author_response.text)
                    author_meta = author_contents["metadata"]
                    author_ids = author_meta["ids"]
                else:
                    author_ids = author["ids"]

                for author_id in author_ids:
                    if author_id["schema"] == "INSPIRE BAI":
                        cls.authors.append(author_id["value"][:-2])

        # published
        if meta["document_type"][0] == "article" and "publication_info" in meta:
            cls.published = meta["publication_info"][0].get("journal_title", "Unpublished")

        if meta["document_type"][0] == "conference paper" and "publication_info" in meta:
            for info in meta["publication_info"]:
                if "cnum" in info:
                    conf_link = info["conference_record"]["$ref"]
                    conf_response = requests.get(conf_link)
                    cls.published = json.loads(conf_response.text)["metadata"]["acronyms"][0]

        # citations
        cls.citations = meta["citation_count"]

        # arxiv id
        cls.arxiv_id = meta["arxiv_eprints"][0]["value"]

        # inspire link
        cls.url = f"https://inspirehep.net/literature/{meta['control_number']}"

        # bibtex
        bibtex_response = requests.get(bibtex_link)
        cls.bibtex = bibtex_response.text[:-1]

        return cls


@dataclass
class NotionPaper:
    Title: Title
    Published: Select
    Authors: Relation
    Citations: Number
    ArxivID: RichText
    CorpusID: RichText
    SemanticURL: URL
    InspireURL: URL
    Bibtex: RichText

    def to_properties(self):
        return {k: v.to_property() for k, v in self.__dict__.items()}
