from __future__ import annotations

from dataclasses import dataclass, field

import requests


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
    def from_response(cls, response: requests.Response):
        meta = response.json()

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


class SemanticEngine:
    def __init__(self):
        self.api = "https://api.semanticscholar.org/graph/v1/paper"

    def retrieve_a_paper(
        self,
        corpus_id: str,
        fields: str = "title,authors,citationCount,journal,externalIds,url",
    ) -> SemanticPaper:
        url = f"{self.api}/CorpusID:{corpus_id}?fields={fields}"
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(response.text)
        else:
            return SemanticPaper.from_response(response)
