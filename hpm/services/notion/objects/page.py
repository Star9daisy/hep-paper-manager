from dataclasses import dataclass, field

from .page_properties import ALL_PAGE_PROPERTIES


@dataclass
class Page:
    id: str | None = None
    url: str | None = None
    parent_id: str | None = None
    properties: dict = field(default_factory=dict)

    @classmethod
    def from_response(cls, data: dict):
        return cls(
            id=data["id"],
            url=data["url"],
            parent_id=data["parent"]["database_id"],
            properties={
                k: ALL_PAGE_PROPERTIES[v["type"]].from_dict(v)
                for k, v in data["properties"].items()
                if v["type"] in ALL_PAGE_PROPERTIES
            },
        )

    @classmethod
    def from_cache(cls, data: dict):
        return cls(
            id=data["id"],
            url=data["url"],
            parent_id=data["parent_id"],
            properties={
                k: ALL_PAGE_PROPERTIES[v["type"]](value=v["value"], id=v["id"])
                for k, v in data["properties"].items()
            },
        )

    def as_dict(self):
        return {
            "id": self.id,
            "url": self.url,
            "parent_id": self.parent_id,
            "properties": {k: v.as_dict() for k, v in self.properties.items()},
        }
