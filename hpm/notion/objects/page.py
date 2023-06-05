from tabulate import tabulate
from ..properties import *


class Page:
    def __init__(
        self,
        page_id: str | None = None,
        parent_id: str | None = None,
        url: str | None = None,
        properties: list[Property] = [],
    ):
        self.page_id = page_id
        self.parent_id = parent_id
        self.url = url
        self.properties = properties

    @property
    def title(self):
        for property in self.properties:
            if property.type == "title":
                return property.value

    @classmethod
    def from_json(cls, response: dict):
        page_id = response["id"]
        parent_id = response["parent"]["database_id"]
        url = response["url"]

        properties = []
        for _name, _property in response["properties"].items():
            _type = _property["type"]
            if _type == "multi_select":
                _object = MultiSelect.from_notion_dict(_name, _property)
            elif _type == "number":
                _object = Number.from_notion_dict(_name, _property)
            elif _type == "relation":
                _object = Relation.from_notion_dict(_name, _property)
            elif _type == "rich_text":
                _object = RichText.from_notion_dict(_name, _property)
            elif _type == "select":
                _object = Select.from_notion_dict(_name, _property)
            elif _type == "title":
                _object = Title.from_notion_dict(_name, _property)
            else:
                continue
            properties.append(_object)

        return cls(page_id, parent_id, url, properties)

    def to_properties(self):
        out = {}
        for property in self.properties:
            out.update(property.to_notion_dict())
        return out

    def get_property(self, name: str):
        target_property = None
        for property in self.properties:
            if property.name == name:
                target_property = property
                break

        if target_property != None:
            return target_property
        else:
            raise ValueError(f"Property {name} not found in this page.")

    def __repr__(self):
        out = ""
        out += f"Page:\n"
        out += f"id: {self.page_id}\n"
        out += f"title: {self.title}\n"
        out += f"parent_id: {self.parent_id}\n"
        out += f"url: {self.url}\n"
        out += f"properties:\n"
        properties = [i.__dict__ for i in self.properties]
        out += tabulate(properties, headers="keys")
        return out
