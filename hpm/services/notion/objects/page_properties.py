from dataclasses import field
from typing import Any, Literal, Self

from pydantic.dataclasses import dataclass


@dataclass
class PageProperty:
    value: Any = None
    id: str | None = None


@dataclass
class Date(PageProperty):
    value: str | None = None
    type: Literal["date"] = "date"

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        return cls(
            value=data["date"]["start"] if data["date"] else None,
            id=data["id"],
        )

    def as_dict(self) -> dict:
        return {"date": {"start": self.value} if self.value else None}


@dataclass
class MultiSelect(PageProperty):
    value: list[str] = field(default_factory=list)
    type: Literal["multi_select"] = "multi_select"

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        return cls(
            value=[i["name"] for i in data["multi_select"]],
            id=data["id"],
        )

    def as_dict(self) -> dict:
        return {"multi_select": [{"name": i} for i in self.value]}


@dataclass
class Number(PageProperty):
    value: int | float | None = None
    type: Literal["number"] = "number"

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        return cls(value=data["number"], id=data["id"])

    def as_dict(self) -> dict:
        return {"number": self.value}


@dataclass
class Relation(PageProperty):
    value: list[str] = field(default_factory=list)
    type: Literal["relation"] = "relation"

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        return cls(value=[i["id"] for i in data["relation"]], id=data["id"])

    def as_dict(self) -> dict:
        return {"relation": [{"id": i} for i in self.value]}


@dataclass
class RichText(PageProperty):
    value: str | None = None
    type: Literal["rich_text"] = "rich_text"

    @classmethod
    def from_dict(cls, property_value: dict) -> Self:
        value = "".join(i["text"]["content"] for i in property_value["rich_text"])
        return cls(value=value or None, id=property_value["id"])

    def as_dict(self) -> dict:
        if self.value is None:
            return {"rich_text": []}

        if len(self.value) >= 2000:
            value = self.value[:1997] + "..."
        else:
            value = self.value

        return {"rich_text": [{"type": "text", "text": {"content": value}}]}


@dataclass
class Select(PageProperty):
    value: str | None = None
    type: Literal["select"] = "select"

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        return cls(
            value=data["select"]["name"] if data["select"] else None,
            id=data["id"],
        )

    def as_dict(self) -> dict:
        if self.value is None:
            return {"select": None}

        return {"select": {"name": self.value}}


@dataclass
class Title(PageProperty):
    value: str | None = None
    type: Literal["title"] = "title"

    @classmethod
    def from_dict(cls, property_value: dict) -> Self:
        value = "".join(i["text"]["content"] for i in property_value["title"])
        return cls(value=value or None, id=property_value["id"])

    def as_dict(self) -> dict:
        if self.value is None:
            return {"title": []}

        return {"title": [{"type": "text", "text": {"content": self.value}}]}


@dataclass
class URL(PageProperty):
    value: str | None = None
    type: Literal["url"] = "url"

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        return cls(value=data["url"], id=data["id"])

    def as_dict(self) -> dict:
        return {"url": self.value}


ALL_PAGE_PROPERTIES = {
    "date": Date,
    "multi_select": MultiSelect,
    "number": Number,
    "relation": Relation,
    "rich_text": RichText,
    "select": Select,
    "title": Title,
    "url": URL,
}
