from __future__ import annotations

from tabulate import tabulate

from ..properties import (
    URL,
    MultiSelect,
    Number,
    Property,
    Relation,
    RichText,
    Select,
    Status,
    Title,
)
from .page import Page


# ---------------------------------------------------------------------------- #
class Database:
    def __init__(
        self,
        id: str,
        title: str,
        description: str,
        url: str,
        properties: list[Property],
        pages: list[Page] = [],
    ) -> None:
        self.id = id
        self.title = title
        self.description = description
        self.url = url
        self.properties = properties
        self.pages = pages

    @classmethod
    def from_json(cls, response: dict):
        _id = response["id"]
        _title = "".join(i["plain_text"] for i in response["title"])
        _description = "".join(i["plain_text"] for i in response["description"])
        _url = response["url"]

        _database_properties = []
        for _name, _property in response["properties"].items():
            _type = _property["type"]
            if _type == "multi_select":
                _object = MultiSelect.from_database_dict(_name, _property)
            elif _type == "number":
                _object = Number.from_notion_dict(_name, _property)
            elif _type == "relation":
                _object = Relation.from_database_dict(_name, _property)
            elif _type == "rich_text":
                _object = RichText.from_notion_dict(_name, _property)
            elif _type == "select":
                _object = Select.from_database_dict(_name, _property)
            elif _type == "status":
                _object = Status.from_notion_dict(_name, _property)
            elif _type == "title":
                _object = Title.from_notion_dict(_name, _property)
            elif _type == "url":
                _object = URL.from_notion_dict(_name, _property)
            else:
                continue
            _database_properties.append(_object)

        return cls(_id, _title, _description, _url, _database_properties)

    def get_property(self, name: str) -> Property:
        for property in self.properties:
            if property.name == name:
                return property

        raise ValueError(f"Property {name} not found in this database")

    def __repr__(self):
        out = ""
        out += f"Database:\n"
        out += f"id: {self.id}\n"
        out += f"title: {self.title}\n"
        out += f"description: {self.description}\n"
        out += f"url: {self.url}\n"
        out += f"properties:\n"
        properties = [i.__dict__ for i in self.properties]
        out += tabulate(properties, headers="keys")
        return out

