from __future__ import annotations

from dataclasses import dataclass
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


class Property(Protocol):
    name: str
    value: Any

    @classmethod
    def from_dict(cls, content) -> Property:
        ...

    def to_dict(self) -> dict:
        ...


@dataclass
class MultiSelect:
    name: str
    value: list[str]

    @classmethod
    def from_dict(cls, content):
        name, property = content
        value = [option["name"] for option in property[property["type"]]["options"]]
        return cls(name, value)

    def to_dict(self):
        return {self.name: {"multi_select": [{"name": option} for option in self.value]}}


@dataclass
class Number:
    name: str
    value: float

    @classmethod
    def from_dict(cls, content):
        name, property = content
        value = property["number"]
        return cls(name, value)

    def to_dict(self):
        return {self.name: {"number": self.value}}


@dataclass
class Relation:
    name: str
    ids: list[str]

    @classmethod
    def from_dict(cls, content):
        name, property = content
        ids = [i["id"] for i in property["relation"]]
        return cls(name, ids)

    def to_dict(self):
        return {self.name: {"relation": [{"id": id} for id in self.ids]}}


@dataclass
class RichText:
    name: str
    value: str

    @classmethod
    def from_dict(cls, content):
        name, property = content
        value = "".join([i["plain_text"] for i in property["rich_text"]])
        return cls(name, value)

    def to_dict(self):
        return {self.name: {"rich_text": [{"text": {"content": self.value}}]}}


@dataclass
class Select:
    name: str
    value: str

    @classmethod
    def from_dict(cls, content):
        name, property = content
        value = property["select"]["name"]
        return cls(name, value)

    def to_dict(self):
        return {self.name: {"select": {"name": self.value}}}


@dataclass
class Title:
    name: str
    value: str

    @classmethod
    def from_dict(cls, content):
        name, property = content
        value = "".join([i["plain_text"] for i in property["title"]])
        return cls(name, value)

    def to_dict(self):
        return {self.name: {"title": [{"text": {"content": self.value}}]}}


@dataclass
class URL:
    name: str
    value: str

    @classmethod
    def from_dict(cls, content):
        name, property = content
        value = property["url"]
        return cls(name, value)

    def to_dict(self):
        return {self.name: {"url": self.value}}
