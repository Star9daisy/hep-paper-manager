from __future__ import annotations

from dataclasses import dataclass, field

import requests


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
    def from_response(cls, response: requests.Response):
        contents = response.json()
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
                    author_contents = author_response.json()
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
                    if "acronyms" in conf_response.json()["metadata"]:
                        cls.published = conf_response.json()["metadata"]["acronyms"][0]
                    elif "alternative_titles" in conf_response.json()["metadata"]:
                        titles = conf_response.json()["metadata"]["alternative_titles"][0]["title"]
                        cls.published = " ".join(titles.split(" ")[1:])

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


class InspireEngine:
    def __init__(self):
        self.api = "https://inspirehep.net/api"

    def retrieve_a_paper(self, arxiv_id) -> InspirePaper:
        url = f"{self.api}/arxiv/{arxiv_id}"
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(response.text)
        else:
            return InspirePaper.from_response(response)
