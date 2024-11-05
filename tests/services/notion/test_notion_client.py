import pytest

# import hpm.services.notion.objects.page_properties as pg_props
import hpm.services.notion.objects.database_properties as db_props
from hpm.services.notion.client import Notion
from hpm.services.notion.objects.page import Page


def test_page():
    client = Notion("secret_t8bapElugK3qKYqQhlub2N0eIwfKw4K69uqCBkhkD4A")

    # Retrieve a page
    data = client.retrieve_page("1271444c50e4806584d2c6ab38a14a87")
    page = Page.from_response(data)
    assert page.as_dict() == {
        "id": "1271444c-50e4-8065-84d2-c6ab38a14a87",
        "url": "https://www.notion.so/1271444c50e4806584d2c6ab38a14a87",
        "parent_id": "1261444c-50e4-808e-83cd-e7c2fe05ded8",
        "properties": {
            "TDate": {"date": None},
            "TNumber": {"number": None},
            "Related papers": {"relation": []},
            "TURL": {"url": None},
            "TMultiSelect": {"multi_select": []},
            "TSelect": {"select": None},
            "TRichText": {"rich_text": []},
            "TName": {"title": []},
        },
    }

    # Create a new page
    data = client.create_page("1261444c50e4808e83cde7c2fe05ded8", page.properties)
    new_page = Page.from_response(data)
    assert new_page.as_dict()["properties"] == {
        "TDate": {"date": None},
        "TNumber": {"number": None},
        "Related papers": {"relation": []},
        "TURL": {"url": None},
        "TMultiSelect": {"multi_select": []},
        "TSelect": {"select": None},
        "TRichText": {"rich_text": []},
        "TName": {"title": []},
    }

    # Update the new page
    new_page.properties["TName"].value = "Test"
    data = client.update_page(new_page.id, new_page.properties)
    updated_page = Page.from_response(data)
    assert updated_page.properties["TName"].value == "Test"

    # Delete the new page
    client.archive_page(new_page.id)


def test_database():
    client = Notion("secret_t8bapElugK3qKYqQhlub2N0eIwfKw4K69uqCBkhkD4A")

    # Query the database
    data = client.query_database("1261444c50e4808e83cde7c2fe05ded8")
    assert len(data["results"]) == 2
    assert data["has_more"] is False

    # Query the database with start cursor
    data = client.query_database("1261444c50e4808e83cde7c2fe05ded8", page_size=1)
    assert len(data["results"]) == 1
    assert data["has_more"] is True

    rest_data = client.query_database(
        "1261444c50e4808e83cde7c2fe05ded8", start_cursor=data["next_cursor"]
    )
    assert len(rest_data["results"]) == 1
    assert rest_data["has_more"] is False

    # Search the database
    response = client.search_database()
    assert len(response["results"]) >= 1

    # Create a database
    response = client.create_database(
        "1271444c50e4808ba7bbc9d0d431c208",
        "TestDataset",
        {"Page title": db_props.Title()},
    )
    client.archive_database(response["id"])


def test_other_cases():
    client = Notion("secret_t8bapElugK3qKYqQhlub2N0eIwfKw4K69uqCBkhkD4A")

    # Retrieve a wrong page
    with pytest.raises(ValueError):
        client.retrieve_page("wrong_id")

    # Create a page with wrong database id
    with pytest.raises(ValueError):
        client.create_page("wrong_id", {})

    # Update a wrong page
    with pytest.raises(ValueError):
        client.update_page("wrong_id", {})

    # Archive a wrong page
    with pytest.raises(ValueError):
        client.archive_page("wrong_id")

    # Query a wrong database
    with pytest.raises(ValueError):
        client.query_database("wrong_id")

    # Retrieve a wrong database
    with pytest.raises(ValueError):
        client.retrieve_database("wrong_id")

    # Search the database with wrong token
    with pytest.raises(ValueError):
        Notion("wrong_token").search_database()

    # Create a database with wrong parent id
    with pytest.raises(ValueError):
        client.create_database(
            "wrong_id", "TestDataset", {"Page title": db_props.Title()}
        )

    # Archive a wrong database
    with pytest.raises(ValueError):
        client.archive_database("wrong_id")
