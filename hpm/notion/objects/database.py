from __future__ import annotations

from dataclasses import dataclass, field

from ..properties import read_property
from .page import Page


@dataclass
class Database:
    id: str
    title: str
    description: str
    url: str
    properties: dict = field(default_factory=dict)
    pages: list[Page | None] = field(default_factory=list)

    @classmethod
    def from_dict(cls, retrieved_json: dict, queried_json: dict) -> Database:
        return cls(
            id=retrieved_json["id"].replace("-", ""),
            title="".join(i["plain_text"] for i in retrieved_json["title"]),
            description="".join(i["plain_text"] for i in retrieved_json["description"]),
            url=retrieved_json["url"],
            properties={
                name: read_property(prop, "database")
                for name, prop in retrieved_json["properties"].items()
            },
            pages=[Page.from_dict(i) for i in queried_json["results"]],
        )
