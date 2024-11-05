import pytest

import hpm.services.notion.objects.database_properties as db_props
import hpm.services.notion.objects.page_properties as pg_props
from hpm.services.notion.client import Notion
from hpm.services.notion.objects.database import Database
from hpm.services.notion.objects.page import Page


def test_basic_usage(TEST_PAGE_ID):
    notion = Notion()

    # Make sure there is at least one database ------------------------------- #
    response = notion.search_database()
    assert len(response["results"]) > 0

    # Create a database without relation property ---------------------------- #
    response = notion.create_database(
        parent_id=TEST_PAGE_ID,
        title="TestDatabase1",
        properties={
            "Date": db_props.Date(),
            "MultiSelect": db_props.MultiSelect(),
            "Number": db_props.Number(),
            "RichText": db_props.RichText(),
            "Select": db_props.Select(),
            "Title": db_props.Title(),
            "URL": db_props.URL(),
        },
    )
    database1 = Database.from_response(response)

    # Validate the database1 is created
    response = notion.retrieve_database(database1.id)
    retrieved_database1 = Database.from_response(response)
    assert database1 == retrieved_database1

    # Create 2 pages in database1 -------------------------------------------- #
    # Page1 has no properties
    response = notion.create_page(parent_id=database1.id, properties={})
    page1 = Page.from_response(response)

    # Validate the Page1 is created
    response = notion.retrieve_page(page1.id)
    retrieved_page1 = Page.from_response(response)
    assert page1 == retrieved_page1

    # Supplement a title to Page1
    response = notion.update_page(page1.id, {"Title": pg_props.Title("Page1")})
    updated_page1 = Page.from_response(response)
    assert updated_page1.title == "Page1"

    # Page2 has all properties
    response = notion.create_page(
        parent_id=database1.id,
        properties={
            "Date": pg_props.Date("2024-11-05"),
            "MultiSelect": pg_props.MultiSelect(["Option1", "Option2"]),
            "Number": pg_props.Number(1.23),
            "RichText": pg_props.RichText("Hello, world!"),
            "Select": pg_props.Select("Option1"),
            "Title": pg_props.Title("Page2"),
            "URL": pg_props.URL("https://www.example.com"),
        },
    )
    page2 = Page.from_response(response)

    # Validate the Page2 is created
    response = notion.retrieve_page(page2.id)
    retrieved_page2 = Page.from_response(response)
    assert page2 == retrieved_page2

    # Validate the 2 pages are in Database1
    response = notion.query_database(database1.id)
    assert len(response["results"]) == 2

    # Or sometimes pages are too many to query all at once
    response = notion.query_database(database1.id, page_size=1)
    assert len(response["results"]) == 1
    assert response["has_more"]

    start_cursor = response["next_cursor"]
    response_next = notion.query_database(database1.id, start_cursor)
    assert len(response_next["results"]) == 1
    assert not response_next["has_more"]

    # Create a database related to Database1 --------------------------------- #
    response = notion.create_database(
        parent_id=TEST_PAGE_ID,
        title="TestDatabase2",
        properties={
            "Relation": db_props.Relation(database1.id),
            "Title": db_props.Title(),
        },
    )
    database2 = Database.from_response(response)

    # Validate the Database2 is created
    response = notion.retrieve_database(database2.id)
    retrieved_database2 = Database.from_response(response)
    assert database2 == retrieved_database2

    # Create a page that relates to Page1 and Page2 in Database1 ------------- #
    response = notion.create_page(
        parent_id=database2.id,
        properties={
            "Relation": pg_props.Relation([page1.id, page2.id]),
            "Title": pg_props.Title("Page"),
        },
    )
    page3 = Page.from_response(response)

    # Validate the Page3 is created
    response = notion.retrieve_page(page3.id)
    retrieved_page3 = Page.from_response(response)
    assert page3 == retrieved_page3

    response = notion.query_database(database2.id)
    assert len(response["results"]) == 1

    # Archive the 3 pages ---------------------------------------------------- #
    notion.archive_page(page1.id)
    notion.archive_page(page2.id)
    notion.archive_page(page3.id)

    # Validate the 3 pages are archived
    assert notion.retrieve_page(page1.id)["archived"]
    assert notion.retrieve_page(page2.id)["archived"]
    assert notion.retrieve_page(page3.id)["archived"]

    response = notion.query_database(database1.id)
    assert len(response["results"]) == 0

    response = notion.query_database(database2.id)
    assert len(response["results"]) == 0

    # Archive the 2 databases ------------------------------------------------ #
    notion.archive_database(database1.id)
    notion.archive_database(database2.id)

    # Validate the 2 databases are archived
    assert notion.retrieve_database(database1.id)["archived"]
    assert notion.retrieve_database(database2.id)["archived"]


def test_other_cases():
    notion = Notion()

    # Retrieve a wrong page
    with pytest.raises(ValueError):
        notion.retrieve_page("wrong_id")

    # Create a page with wrong database id
    with pytest.raises(ValueError):
        notion.create_page("wrong_id", {})

    # Update a wrong page
    with pytest.raises(ValueError):
        notion.update_page("wrong_id", {})

    # Archive a wrong page
    with pytest.raises(ValueError):
        notion.archive_page("wrong_id")

    # Query a wrong database
    with pytest.raises(ValueError):
        notion.query_database("wrong_id")

    # Retrieve a wrong database
    with pytest.raises(ValueError):
        notion.retrieve_database("wrong_id")

    # Search the database with wrong token
    with pytest.raises(ValueError):
        Notion("wrong_token").search_database()

    # Create a database with wrong parent id
    with pytest.raises(ValueError):
        notion.create_database(
            "wrong_id", "TestDataset", {"Page title": db_props.Title()}
        )

    # Archive a wrong database
    with pytest.raises(ValueError):
        notion.archive_database("wrong_id")
