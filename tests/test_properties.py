import json

from hpm.notion.properties import *

with open("tests/property_examples.json", "r") as f:
    examples = json.load(f)


def test_multi_select_get():
    example = examples["multi_select"]["get"]
    expected = MultiSelect(
        name="Programming language",
        value=["TypeScript", "JavaScript", "Python"],
    )
    for content in example.items():
        multi_select = MultiSelect.from_dict(content)

    assert multi_select.from_dict(content) == expected


def test_multi_select_post():
    expected = examples["multi_select"]["post"]
    multi_select = MultiSelect(name="Programming language", value=["TypeScript", "Python"])

    assert multi_select.to_dict() == expected


def test_number_get():
    example = examples["number"]["get"]
    expected = Number(name="Number of subscribers", value=1234)
    for content in example.items():
        number = Number.from_dict(content)

    assert number.from_dict(content) == expected


def test_number_post():
    expected = examples["number"]["post"]
    number = Number(name="Number of subscribers", value=42)

    assert number.to_dict() == expected


def test_relation_get():
    example = examples["relation"]["get"]
    expected = Relation(
        name="Related tasks",
        ids=["dd456007-6c66-4bba-957e-ea501dcda3a6", "0c1f7cb2-8090-4f18-924e-d92965055e32"],
    )
    for content in example.items():
        relation = Relation.from_dict(content)

    assert relation.from_dict(content) == expected


def test_relation_post():
    expected = examples["relation"]["post"]
    relation = Relation(
        name="Related tasks",
        ids=["dd456007-6c66-4bba-957e-ea501dcda3a6", "0c1f7cb2-8090-4f18-924e-d92965055e32"],
    )

    assert relation.to_dict() == expected


def test_rich_text_get():
    example = examples["rich_text"]["get"]
    expected = RichText(name="Description", value="There is some text in this property!")
    for content in example.items():
        rich_text = RichText.from_dict(content)

    assert rich_text.from_dict(content) == expected


def test_rich_text_post():
    expected = examples["rich_text"]["post"]
    rich_text = RichText(name="Description", value="There is some text in this property!")

    assert rich_text.to_dict() == expected


def test_select_get():
    example = examples["select"]["get"]
    expected = Select(name="Department", value="jQuery")
    for content in example.items():
        select = Select.from_dict(content)

    assert select.from_dict(content) == expected


def test_select_post():
    expected = examples["select"]["post"]
    select = Select(name="Department", value="Marketing")

    assert select.to_dict() == expected


def test_title_get():
    example = examples["title"]["get"]
    expected = Title(name="Title", value="A better title for the page")
    for content in example.items():
        title = Title.from_dict(content)

    assert title.from_dict(content) == expected


def test_title_post():
    expected = examples["title"]["post"]
    title = Title(name="Title", value="A better title for the page")

    assert title.to_dict() == expected


def test_url_get():
    example = examples["url"]["get"]
    expected = URL(name="Website", value="https://developers.notion.com/")
    for content in example.items():
        url = URL.from_dict(content)

    assert url.from_dict(content) == expected


def test_url_post():
    expected = examples["url"]["post"]
    url = URL(name="Website", value="https://developers.notion.com/")

    assert url.to_dict() == expected
