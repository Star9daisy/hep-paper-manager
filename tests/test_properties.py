import json

from hpm.notion.properties import *

with open("tests/property_examples.json", "r") as f:
    examples = json.load(f)


def test_multi_select():
    property0 = {
        "id": "n%3A%7Cb",
        "type": "multi_select",
        "multi_select": [],
    }
    property1 = {
        "id": "n%3A%7Cb",
        "type": "multi_select",
        "multi_select": [
            {"id": "f380fd0b-a8ea-4431-a943-86a49779af6a", "name": "tag1", "color": "yellow"},
            {"id": "2e50375c-3fe2-4356-b6cf-f058ff661920", "name": "tag2", "color": "blue"},
        ],
    }
    expected0 = MultiSelect()
    expected1 = MultiSelect(["tag1", "tag2"])

    multi_select0 = MultiSelect.from_dict(property0)
    multi_select1 = MultiSelect.from_dict(property1)

    assert multi_select0 == expected0
    assert multi_select1 == expected1

    expected0 = {"multi_select": []}
    expected1 = {"multi_select": [{"name": "tag1"}, {"name": "tag2"}]}

    assert multi_select0.to_dict() == expected0
    assert multi_select1.to_dict() == expected1


def test_number():
    property0 = {"id": "cznt", "type": "number", "number": None}
    property1 = {"id": "cznt", "type": "number", "number": 1}
    expected0 = Number()
    expected1 = Number(1)
    number0 = Number.from_dict(property0)
    number1 = Number.from_dict(property1)
    assert number0 == expected0
    assert number1 == expected1

    expected0 = {"number": None}
    expected1 = {"number": 1}
    assert number0.to_dict() == expected0
    assert number1.to_dict() == expected1


def test_relation():
    property0 = {
        "id": "f%7D%7CZ",
        "type": "relation",
        "relation": [],
        "has_more": False,
    }
    property1 = {
        "id": "f%7D%7CZ",
        "type": "relation",
        "relation": [
            {"id": "633144dd-78bf-4fe6-800e-83a530c3d87e"},
            {"id": "eda17f33-9aa2-4341-b6ab-07bdf0e55b24"},
            {"id": "3f4ce0fd-dde2-4c8f-b301-2905170c2034"},
        ],
        "has_more": False,
    }
    expected0 = Relation()
    expected1 = Relation(
        [
            "633144dd78bf4fe6800e83a530c3d87e",
            "eda17f339aa24341b6ab07bdf0e55b24",
            "3f4ce0fddde24c8fb3012905170c2034",
        ]
    )
    relation0 = Relation.from_dict(property0)
    relation1 = Relation.from_dict(property1)
    assert relation0 == expected0
    assert relation1 == expected1

    expected0 = {"relation": []}
    expected1 = {
        "relation": [
            {"id": "633144dd78bf4fe6800e83a530c3d87e"},
            {"id": "eda17f339aa24341b6ab07bdf0e55b24"},
            {"id": "3f4ce0fddde24c8fb3012905170c2034"},
        ]
    }
    assert relation0.to_dict() == expected0
    assert relation1.to_dict() == expected1


def test_rich_text():
    property0 = {"id": "vBGj", "type": "rich_text", "rich_text": []}
    property1 = {
        "id": "vBGj",
        "type": "rich_text",
        "rich_text": [
            {
                "type": "text",
                "text": {"content": "This is a rich text property", "link": None},
                "annotations": {
                    "bold": False,
                    "italic": False,
                    "strikethrough": False,
                    "underline": False,
                    "code": False,
                    "color": "default",
                },
                "plain_text": "This is a rich text property",
                "href": None,
            }
        ],
    }
    expected0 = RichText()
    expected1 = RichText("This is a rich text property")
    rich_text0 = RichText.from_dict(property0)
    rich_text1 = RichText.from_dict(property1)
    assert rich_text0 == expected0
    assert rich_text1 == expected1

    expected0 = {"rich_text": [{"text": {"content": ""}}]}
    expected1 = {"rich_text": [{"text": {"content": "This is a rich text property"}}]}
    assert rich_text0.to_dict() == expected0
    assert rich_text1.to_dict() == expected1


def test_select():
    property0 = {"id": "K%3B%3ED", "type": "select", "select": None}
    property1 = {
        "id": "K%3B%3ED",
        "type": "select",
        "select": {"id": "562bd134-3486-4236-828d-df1fe8d2614f", "name": "topic1", "color": "gray"},
    }
    expected0 = Select()
    expected1 = Select("topic1")
    select0 = Select.from_dict(property0)
    select1 = Select.from_dict(property1)
    assert select0 == expected0
    assert select1 == expected1

    expected0 = {"select": None}
    expected1 = {"select": {"name": "topic1"}}
    assert select0.to_dict() == expected0
    assert select1.to_dict() == expected1


def test_title():
    property0 = {"id": "title", "type": "title", "title": []}
    property1 = {
        "id": "title",
        "type": "title",
        "title": [
            {
                "type": "text",
                "text": {"content": "Item1", "link": None},
                "annotations": {
                    "bold": False,
                    "italic": False,
                    "strikethrough": False,
                    "underline": False,
                    "code": False,
                    "color": "default",
                },
                "plain_text": "Item1",
                "href": None,
            }
        ],
    }
    expected0 = Title()
    expected1 = Title("Item1")
    title0 = Title.from_dict(property0)
    title1 = Title.from_dict(property1)
    assert title0 == expected0
    assert title1 == expected1

    expected0 = {"title": [{"text": {"content": ""}}]}
    expected1 = {"title": [{"text": {"content": "Item1"}}]}
    assert title0.to_dict() == expected0
    assert title1.to_dict() == expected1


def test_url():
    property0 = {"id": "HCl%3D", "type": "url", "url": None}
    property1 = {
        "id": "HCl%3D",
        "type": "url",
        "url": "https://developers.notion.com/reference/property-object",
    }
    expected0 = URL()
    expected1 = URL("https://developers.notion.com/reference/property-object")
    url0 = URL.from_dict(property0)
    url1 = URL.from_dict(property1)
    assert url0 == expected0
    assert url1 == expected1

    expected0 = {"url": None}
    expected1 = {"url": "https://developers.notion.com/reference/property-object"}
    assert url0.to_dict() == expected0
    assert url1.to_dict() == expected1
