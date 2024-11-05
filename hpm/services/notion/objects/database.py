from dataclasses import dataclass, field

from .database_properties import ALL_DATABASE_PROPERTIES, DatabaseProperty


@dataclass
class Database:
    id: str | None = None
    title: str | None = None
    url: str | None = None
    properties: dict[str, DatabaseProperty] = field(default_factory=dict)

    @classmethod
    def from_response(cls, data: dict):
        return cls(
            id=data["id"],
            title=data["title"][0]["text"]["content"],
            url=data["url"],
            properties={
                k: ALL_DATABASE_PROPERTIES[v["type"]].from_dict(v)
                for k, v in data["properties"].items()
                if v["type"] in ALL_DATABASE_PROPERTIES
            },
        )
