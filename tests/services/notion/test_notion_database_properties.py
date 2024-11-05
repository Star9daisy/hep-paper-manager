from hpm.services.notion.objects.database_properties import (
    URL,
    Date,
    MultiSelect,
    Number,
    Relation,
    RichText,
    Select,
    Title,
)


def test_date():
    property = Date()
    assert property.as_dict() == {"date": {}}


def test_multi_select():
    property = MultiSelect()
    assert property.as_dict() == {"multi_select": {}}


def test_number():
    property = Number()
    assert property.as_dict() == {"number": {}}


def test_relation():
    property = Relation()
    assert property.as_dict() == {"relation": {}}

    property = Relation(["id1", "id2"])
    assert property.as_dict() == {
        "relation": {"database_id": ["id1", "id2"], "single_property": {}}
    }


def test_rich_text():
    property = RichText()
    assert property.as_dict() == {"rich_text": {}}


def test_select():
    property = Select()
    assert property.as_dict() == {"select": {}}


def test_title():
    property = Title()
    assert property.as_dict() == {"title": {}}


def test_url():
    property = URL()
    assert property.as_dict() == {"url": {}}
