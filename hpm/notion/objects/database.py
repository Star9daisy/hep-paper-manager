from tabulate import tabulate
from ..properties import *
from .page import Page


class Database:
    def __init__(
        self,
        database_id: str,
        title: str,
        description: str,
        url: str,
        properties: list[Property],
        pages: list[Page] = [],
    ) -> None:
        self.database_id = database_id
        self.title = title
        self.description = description
        self.url = url
        self.properties = properties
        self.pages = pages

    @classmethod
    def from_json(cls, response: dict):
        database_id = response["id"]
        title = "".join(i["plain_text"] for i in response["title"])
        description = "".join(i["plain_text"] for i in response["description"])
        url = response["url"]

        properties = []
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
            elif _type == "title":
                _object = Title.from_notion_dict(_name, _property)
            else:
                continue
            properties.append(_object)

        return cls(database_id, title, description, url, properties)

    def get_property(self, name: str) -> Property:
        for property in self.properties:
            if property.name == name:
                return property

        raise ValueError(f"Property {name} not found in this database")
