from __future__ import annotations

from dataclasses import asdict, dataclass, field

import requests
from typing_extensions import Literal, Self


@dataclass
class Author:
    id: str | None = None
    url: str | None = None
    name: str | None = None
    institutions: list[str] = field(default_factory=list)

    @classmethod
    def from_response(cls, data: dict) -> Self:
        metadata = data["metadata"]

        author = cls()
        author.id = str(metadata["control_number"])
        author.url = f"https://inspirehep.net/authors/{author.id}"

        if "preferred_name" in metadata["name"]:
            author.name = metadata["name"]["preferred_name"]
        else:
            # This name may contain a comma which is not valid in Notion selection
            author.name = metadata["name"]["value"]
            author.name = " ".join(author.name.split(", ")[::-1])

        for position in metadata.get("positions", []):
            if position.get("current") is True:
                author.institutions.append(position["institution"])

        return author

    @classmethod
    def from_cache(cls, data: dict) -> Self:
        return cls(**data)

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass
class Paper:
    id: str | None = None
    url: str | None = None
    type: str | None = None
    source: Literal["Inspire HEP"] = "Inspire HEP"
    title: str | None = None
    authors: list[Author] = field(default_factory=list)
    created_date: str | None = None
    published_place: str | None = None
    published_date: str | None = None
    eprint: str | None = None
    citation_count: int | None = None
    abstract: str | None = None
    doi: str | None = None
    bibtex: str | None = None

    @classmethod
    def from_response(cls, data: dict) -> Self:
        metadata = data["metadata"]

        paper = cls()
        paper.id = str(metadata["control_number"])
        paper.url = f"https://inspirehep.net/literature/{paper.id}"
        paper.type = metadata["document_type"][0]
        paper.title = metadata["titles"][0]["title"]

        for author_info in metadata["authors"][:10]:
            author = Author()
            author.id = author_info["record"]["$ref"].split("/")[-1]
            author.url = f"https://inspirehep.net/authors/{author.id}"
            author.name = " ".join(author_info["full_name"].split(", ")[::-1])
            paper.authors.append(author)

        if metadata["preprint_date"].count("-") == 2:
            paper.created_date = metadata["preprint_date"]
        else:
            paper.created_date = data["created"].split("T")[0]

        if "publication_info" in metadata:
            paper.published_place = metadata["publication_info"][0].get("journal_title")

        if "imprints" in metadata:
            paper.published_date = metadata["imprints"][0]["date"]

        paper.eprint = metadata["arxiv_eprints"][0]["value"]
        paper.citation_count = metadata["citation_count"]

        abstract = metadata["abstracts"][0]["value"]
        if len(abstract) > 2000:
            abstract = abstract[:1997] + "..."
        paper.abstract = abstract

        paper.doi = metadata.get("dois", [{}])[0].get("value")

        bibtex_link = data["links"]["bibtex"]
        bibtex_response = requests.get(bibtex_link)
        paper.bibtex = bibtex_response.text[:-1]

        return paper

    @classmethod
    def from_cache(cls, data: dict) -> Self:
        authors = [Author.from_cache(a) for a in data.pop("authors")]
        return cls(authors=authors, **data)

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass
class Job:
    id: str | None = None
    url: str | None = None
    position: str | None = None
    institutions: list[str] = field(default_factory=list)
    regions: list[str] = field(default_factory=list)
    ranks: list[str] = field(default_factory=list)
    deadline: str | None = None
    created_date: str | None = None
    updated_date: str | None = None
    description: str | None = None

    @classmethod
    def from_response(cls, data: dict) -> Self:
        meta = data["metadata"]

        job = cls()
        job.id = data["id"]
        job.url = f"https://inspirehep.net/jobs/{data['id']}"
        job.position = meta.get("position")
        job.institutions = [i["value"] for i in meta.get("institutions", [])]
        job.regions = meta.get("regions", [])
        job.ranks = meta.get("ranks", [])
        job.deadline = meta.get("deadline_date")
        job.created_date = data["created"].split("T")[0]
        job.updated_date = data["updated"].split("T")[0]
        job.description = (
            meta["description"]
            .replace("<br>", "")
            .replace("<div>", "")
            .replace("</div>", "\n")
            .replace("&nbsp;", " ")
            .replace("<strong>", "**")
            .replace("</strong>", "**")
            .replace('<a href="', "[")
            .replace('">', "](")
            .replace("</a>", ")")
        )

        return job

    @classmethod
    def from_cache(cls, data: dict) -> Self:
        return cls(**data)

    def as_dict(self) -> dict:
        return asdict(self)
