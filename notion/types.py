from typing import NamedTuple


class Title(NamedTuple):
    content: str

    def to_property(self):
        return {"title": [{"text": {"content": self.content}}]}


class Select(NamedTuple):
    name: str

    def to_property(self):
        return {"select": {"name": self.name}}


class Number(NamedTuple):
    number: float

    def to_property(self):
        return {"number": self.number}


class RichText(NamedTuple):
    content: str

    def to_property(self):
        return {"rich_text": [{"text": {"content": self.content}}]}


class URL(NamedTuple):
    url: str

    def to_property(self):
        return {"url": self.url}


class Relation(NamedTuple):
    ids: list[str]

    def to_property(self):
        return {"relation": [{"id": id} for id in self.ids]}
