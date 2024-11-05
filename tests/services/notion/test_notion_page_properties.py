import json

import pytest

from hpm.services.notion.objects.page_properties import (
    URL,
    Date,
    MultiSelect,
    Number,
    Relation,
    RichText,
    Select,
    Title,
)


@pytest.fixture
def test_full_page():
    return json.load(open("tests/services/notion/full_page.json", "r"))


@pytest.fixture
def test_empty_page():
    return json.load(open("tests/services/notion/empty_page.json", "r"))


def test_date(test_full_page, test_empty_page):
    # Test full page
    expected = Date.from_dict(test_full_page["properties"]["TDate"])
    property = Date("2024-10-28")

    assert property.value == expected.value
    assert property.as_dict() == expected.as_dict()

    # Test empty page
    expected = Date.from_dict(test_empty_page["properties"]["TDate"])
    property = Date()

    assert property.value == expected.value
    assert property.as_dict() == expected.as_dict()


def test_multi_select(test_full_page, test_empty_page):
    # Test full page
    expected = MultiSelect.from_dict(test_full_page["properties"]["TMultiSelect"])
    property = MultiSelect(["TestOption", "Option 1", "Option 2"])

    assert property.value == expected.value
    assert property.as_dict() == expected.as_dict()

    # Test empty page
    expected = MultiSelect.from_dict(test_empty_page["properties"]["TMultiSelect"])
    property = MultiSelect()

    assert property.value == expected.value
    assert property.as_dict() == expected.as_dict()


def test_number(test_full_page, test_empty_page):
    # Test full page
    expected = Number.from_dict(test_full_page["properties"]["TNumber"])
    property = Number(100)

    assert property.value == expected.value
    assert property.as_dict() == expected.as_dict()

    # Test empty page
    expected = Number.from_dict(test_empty_page["properties"]["TNumber"])
    property = Number()

    assert property.value == expected.value
    assert property.as_dict() == expected.as_dict()


def test_relation(test_full_page, test_empty_page):
    # Test full page
    expected = Relation.from_dict(test_full_page["properties"]["Related papers"])
    property = Relation(
        ["1321444c-50e4-81ca-8f8d-d4a4503830e9", "1321444c-50e4-8129-8a43-d85bdad7414c"]
    )

    assert property.value == expected.value
    assert property.as_dict() == expected.as_dict()

    # Test empty page
    expected = Relation.from_dict(test_empty_page["properties"]["Related papers"])
    property = Relation()

    assert property.value == expected.value
    assert property.as_dict() == expected.as_dict()


def test_rich_text(test_full_page, test_empty_page):
    # Test full page
    expected = RichText.from_dict(test_full_page["properties"]["TRichText"])
    property = RichText("test")

    assert property.value == expected.value
    assert property.as_dict() == expected.as_dict()

    # Test empty page
    expected = RichText.from_dict(test_empty_page["properties"]["TRichText"])
    property = RichText()

    assert property.value == expected.value
    assert property.as_dict() == expected.as_dict()

    # Test long value
    property = RichText("x" * 2000)

    assert property.value == "x" * 2000
    assert property.as_dict() == {
        "rich_text": [{"type": "text", "text": {"content": "x" * 1997 + "..."}}]
    }


def test_select(test_full_page, test_empty_page):
    # Test full page
    expected = Select.from_dict(test_full_page["properties"]["TSelect"])
    property = Select("testtag")

    assert property.value == expected.value
    assert property.as_dict() == expected.as_dict()

    # Test empty page
    expected = Select.from_dict(test_empty_page["properties"]["TSelect"])
    property = Select()

    assert property.value == expected.value
    assert property.as_dict() == expected.as_dict()


def test_title(test_full_page, test_empty_page):
    # Test full page
    expected = Title.from_dict(test_full_page["properties"]["TName"])
    property = Title("test")

    assert property.value == expected.value
    assert property.as_dict() == expected.as_dict()

    # Test empty page
    expected = Title.from_dict(test_empty_page["properties"]["TName"])
    property = Title()

    assert property.value == expected.value
    assert property.as_dict() == expected.as_dict()


def test_url(test_full_page, test_empty_page):
    # Test full page
    expected = URL.from_dict(test_full_page["properties"]["TURL"])
    property = URL("example.com")

    assert property.value == expected.value
    assert property.as_dict() == expected.as_dict()

    # Test empty page
    expected = URL.from_dict(test_empty_page["properties"]["TURL"])
    property = URL()

    assert property.value == expected.value
    assert property.as_dict() == expected.as_dict()
