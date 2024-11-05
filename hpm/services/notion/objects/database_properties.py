from typing import Any, Literal, Self

from pydantic.dataclasses import dataclass


@dataclass
class DatabaseProperty:
    value: Any = None
    id: str | None = None

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        return cls(id=data["id"])


@dataclass
class Date(DatabaseProperty):
    type: Literal["date"] = "date"

    def as_dict(self) -> dict:
        return {"date": {}}


@dataclass
class MultiSelect(DatabaseProperty):
    type: Literal["multi_select"] = "multi_select"

    def as_dict(self) -> dict:
        return {"multi_select": {}}


@dataclass
class Number(DatabaseProperty):
    type: Literal["number"] = "number"

    def as_dict(self):
        return {"number": {}}


@dataclass
class Relation(DatabaseProperty):
    type: Literal["relation"] = "relation"

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            value=data["relation"]["database_id"].replace("-", ""), id=data["id"]
        )

    def as_dict(self):
        if self.value is None:
            return {"relation": {}}

        return {"relation": {"database_id": self.value, "single_property": {}}}


@dataclass
class RichText(DatabaseProperty):
    type: Literal["rich_text"] = "rich_text"

    def as_dict(self):
        return {"rich_text": {}}


@dataclass
class Select(DatabaseProperty):
    type: Literal["select"] = "select"

    def as_dict(self):
        return {"select": {}}


@dataclass
class Title(DatabaseProperty):
    type: Literal["title"] = "title"

    def as_dict(self):
        return {"title": {}}


@dataclass
class URL(DatabaseProperty):
    type: Literal["url"] = "url"

    def as_dict(self):
        return {"url": {}}


ALL_DATABASE_PROPERTIES = {
    "date": Date,
    "multi_select": MultiSelect,
    "number": Number,
    "relation": Relation,
    "rich_text": RichText,
    "select": Select,
    "title": Title,
    "url": URL,
}
