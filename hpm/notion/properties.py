from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

__all__ = [
    "MultiSelect",
    "Number",
    "Relation",
    "RichText",
    "Select",
    "Title",
    "URL",
]


def read_property(property: dict, source: str = "page") -> Property:
    if source == "page":
        property_type_to_class = {
            "multi_select": MultiSelect,
            "number": Number,
            "relation": Relation,
            "rich_text": RichText,
            "select": Select,
            "title": Title,
            "url": URL,
        }
    elif source == "database":
        property_type_to_class = {
            "multi_select": DatabaseMultiSelect,
            "number": DatabaseNumber,
            "relation": DatabaseRelation,
            "rich_text": DatabaseRichText,
            "select": DatabaseSelect,
            "title": DatabaseTitle,
            "url": DatabaseURL,
        }
    else:
        raise ValueError(f"Invalid source: {source}, choose 'page' or 'database'")

    return property_type_to_class[property["type"]].from_dict(property)


class Property(Protocol):
    value: Any

    @classmethod
    def from_dict(cls, property: dict) -> Property:
        ...

    def to_dict(self) -> dict:
        ...


@dataclass
class MultiSelect:
    value: list[str | None] = field(default_factory=list)

    @classmethod
    def from_dict(cls, property: dict):
        options = property["multi_select"]
        value = [option["name"] for option in options] if options else []
        return cls(value)

    def to_dict(self):
        return {"multi_select": [{"name": option} for option in self.value]}


@dataclass
class DatabaseMultiSelect:
    value: list[str | None] = field(default_factory=list)

    @classmethod
    def from_dict(cls, property: dict):
        options = property["multi_select"]["options"]
        value = [option["name"] for option in options] if options else []
        return cls(value)


@dataclass
class Number:
    value: float | None = None

    @classmethod
    def from_dict(cls, property: dict):
        value = property["number"]
        return cls(value)

    def to_dict(self):
        return {"number": self.value}


@dataclass
class DatabaseNumber:
    value: str

    @classmethod
    def from_dict(cls, property: dict):
        value = property["number"]["format"]
        return cls(value)


@dataclass
class Relation:
    value: list[str | None] = field(default_factory=list)

    @classmethod
    def from_dict(cls, property: dict):
        relations = property["relation"]
        value = [i["id"].replace("-", "") for i in relations] if relations else []
        return cls(value)

    def to_dict(self):
        return {"relation": [{"id": i} for i in self.value]}


@dataclass
class DatabaseRelation:
    value: str

    @classmethod
    def from_dict(cls, property: dict):
        value = property["relation"]["database_id"].replace("-", "")
        return cls(value)


@dataclass
class RichText:
    value: str = ""

    @classmethod
    def from_dict(cls, property: dict):
        content = property["rich_text"]
        value = "".join([i["plain_text"] for i in content]) if content else ""
        return cls(value)

    def to_dict(self):
        return {"rich_text": [{"text": {"content": self.value}}]}


@dataclass
class DatabaseRichText:
    value: str = ""

    @classmethod
    def from_dict(cls, property: dict):
        return cls("")


@dataclass
class Select:
    value: str | None = None

    @classmethod
    def from_dict(cls, property: dict):
        selection = property["select"]
        value = selection["name"] if selection else None
        return cls(value)

    def to_dict(self):
        if self.value:
            return {"select": {"name": self.value}}
        else:
            return {"select": None}


@dataclass
class DatabaseSelect:
    value: list[str | None] = field(default_factory=list)

    @classmethod
    def from_dict(cls, property: dict):
        options = property["select"]["options"]
        value = [option["name"] for option in options] if options else []
        return cls(value)


@dataclass
class Title:
    value: str = ""

    @classmethod
    def from_dict(cls, property):
        content = property["title"]
        value = "".join([i["plain_text"] for i in content]) if content else ""
        return cls(value)

    def to_dict(self):
        return {"title": [{"text": {"content": self.value}}]}


@dataclass
class DatabaseTitle:
    value: str = ""

    @classmethod
    def from_dict(cls, property: dict):
        return cls("")


@dataclass
class URL:
    value: str | None = None

    @classmethod
    def from_dict(cls, property: dict):
        value = property["url"]
        return cls(value)

    def to_dict(self):
        return {"url": self.value}


@dataclass
class DatabaseURL:
    value: str = ""

    @classmethod
    def from_dict(cls, property: dict):
        return cls("")
