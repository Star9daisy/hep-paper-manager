from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

__all__ = [
    "Property",
    "MultiSelect",
    "Number",
    "Relation",
    "RichText",
    "Select",
    "Title",
    # "URL",
]


# ---------------------------------------------------------------------------- #
class Property(ABC):
    name: str
    type: str
    value: Any

    @classmethod
    @abstractmethod
    def from_notion_dict(cls, name, property: dict) -> Property:
        ...

    @abstractmethod
    def to_notion_dict(self) -> dict[str, Any]:
        ...


@dataclass
class MultiSelect(Property):
    name: str
    value: list[str]
    type: str = "multi_select"

    @classmethod
    def from_database_dict(cls, name, property):
        options = [option["name"] for option in property["multi_select"]["options"]]
        return cls(name, options)

    @classmethod
    def from_notion_dict(cls, name, property):
        value = [option["name"] for option in property["multi_select"]]
        return cls(name, value)

    def to_notion_dict(self):
        return {self.name: {"multi_select": [{"name": i} for i in self.value]}}


@dataclass
class Number(Property):
    name: str
    value: float
    type: str = "number"

    @classmethod
    def from_notion_dict(cls, name, property):
        return cls(name, property["number"])

    def to_notion_dict(self):
        return {self.name: {"number": self.value}}


@dataclass
class Relation(Property):
    name: str
    value: list[str] | str
    type: str = "relation"

    @classmethod
    def from_database_dict(cls, name, property):
        database_id = property["relation"]["database_id"]
        return cls(name, database_id)

    @classmethod
    def from_notion_dict(cls, name, property):
        ids = [relation["id"] for relation in property["relation"]]
        return cls(name, ids)

    def to_notion_dict(self):
        return {self.name: {"relation": [{"id": id} for id in self.value]}}


@dataclass
class RichText(Property):
    name: str
    value: str
    type: str = "rich_text"

    @classmethod
    def from_notion_dict(cls, name, property):
        content = "".join([part["plain_text"] for part in property["rich_text"]])
        return cls(name, content)

    def to_notion_dict(self):
        return {self.name: {"rich_text": [{"text": {"content": self.value}}]}}


@dataclass
class Select(Property):
    name: str
    value: list[str] | str | None = None
    type: str = "select"

    @classmethod
    def from_database_dict(cls, name, property):
        options = [option["name"] for option in property["select"]["options"]]
        return cls(name, options)

    @classmethod
    def from_notion_dict(cls, name, property):
        if property["select"]:
            value = property["select"]["name"]
        else:
            value = None
        return cls(name, value)

    def to_notion_dict(self):
        if self.value:
            return {self.name: {"select": {"name": self.value}}}
        else:
            return {self.name: {"select": None}}


@dataclass
class Title(Property):
    name: str
    value: str
    type: str = "title"

    @classmethod
    def from_notion_dict(cls, name, property):
        content = "".join([part["plain_text"] for part in property["title"]])
        return cls(name, content)

    def to_notion_dict(self):
        return {self.name: {"title": [{"text": {"content": self.value}}]}}


@dataclass
class URL(Property):
    name: str
    value: str
    type: str = "url"

    @classmethod
    def from_notion_dict(cls, name, property):
        return cls(name, property["url"])

    def to_notion_dict(self):
        return {self.name: {"url": self.value}}
