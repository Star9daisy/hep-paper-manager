import os

from dotenv import load_dotenv

from hpm.notion import Client
from hpm.notion.objects import Page
from hpm.notion.properties import *

load_dotenv(".env")
token = os.getenv("TOKEN")
client = Client(token)


def test_retrieve_page():
    expected_01 = Page(
        id="633144dd78bf4fe6800e83a530c3d87e",
        parent_id="480d39ea2a6d49d3a6e9af7b2aed8152",
        properties=[
            RichText(name="ID", value="01"),
            Select(name="Journal", value="JournalA"),
            Number(name="Citations", value=90),
            Title(name="Title", value="Paper with title 1"),
        ],
        url="https://www.notion.so/Paper-with-title-1-633144dd78bf4fe6800e83a530c3d87e",
    )
    page_01 = client.retrieve_page("633144dd78bf4fe6800e83a530c3d87e")
    assert page_01 == expected_01

    expected_02 = Page(
        id="eda17f339aa24341b6ab07bdf0e55b24",
        parent_id="480d39ea2a6d49d3a6e9af7b2aed8152",
        properties=[
            RichText(name="ID", value="02"),
            Select(name="Journal", value="JournalB"),
            Number(name="Citations", value=20),
            Title(name="Title", value="Paper with title 2"),
        ],
        url="https://www.notion.so/Paper-with-title-2-eda17f339aa24341b6ab07bdf0e55b24",
    )
    page_02 = client.retrieve_page("eda17f339aa24341b6ab07bdf0e55b24")
    assert page_02 == expected_02

    expected_03 = Page(
        id="3f4ce0fddde24c8fb3012905170c2034",
        parent_id="480d39ea2a6d49d3a6e9af7b2aed8152",
        properties=[
            RichText(name="ID", value="03"),
            Select(name="Journal", value="JournalC"),
            Number(name="Citations", value=5),
            Title(name="Title", value="Paper with title 3"),
        ],
        url="https://www.notion.so/Paper-with-title-3-3f4ce0fddde24c8fb3012905170c2034",
    )
    page_03 = client.retrieve_page("3f4ce0fddde24c8fb3012905170c2034")
    assert page_03 == expected_03


def test_update_page():
    page_01 = client.retrieve_page("633144dd78bf4fe6800e83a530c3d87e")
    page_01.set_property("ID", "1234")

    new_page_01 = client.update_page(page_01)
    assert new_page_01.get_property("ID") == "1234"

    new_page_01.set_property("ID", "01")
    old_page_01 = client.update_page(new_page_01)
    assert old_page_01 == new_page_01


def test_create_archive_restore_page():
    page = Page(
        id=None,
        parent_id="480d39ea2a6d49d3a6e9af7b2aed8152",
        properties=[
            RichText(name="ID", value="04"),
            Number(name="Citations", value=0),
            Title(name="Title", value="Paper with title 4"),
        ],
        url=None,
    )

    new_page = client.create_page(page, page.parent_id)
    assert new_page.get_property("ID") == "04"
    assert new_page.get_property("Citations") == 0
    assert new_page.get_property("Title") == "Paper with title 4"
    assert new_page.get_property("Journal") == None

    archived_page = client.archive_page(new_page)
    assert archived_page == new_page

    restored_page = client.restore_page(archived_page)
    assert restored_page == archived_page

    client.archive_page(restored_page)
