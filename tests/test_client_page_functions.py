import os

from dotenv import load_dotenv

from hpm.notion import Client
from hpm.notion.objects import Page
from hpm.notion.properties import *

load_dotenv(".env")
token = os.getenv("TOKEN")
client = Client(token)
parent_id = "19ef8e6eab3542aa91a2f4aa54623479"
page_id0 = "d18e78e482e94a3995c18e1932ae9fb8"
page_id1 = "48cb3c1ee9664680884dd7bfa05913a3"


def test_retrieve_page():
    expected0 = Page(
        parent_id="19ef8e6eab3542aa91a2f4aa54623479",
        properties={
            "p_url": URL(value=None),
            "p_select": Select(value=None),
            "p_number": Number(value=None),
            "p_relation": Relation(value=[]),
            "p_multi_select": MultiSelect(value=[]),
            "p_rich_text": RichText(value=""),
            "p_title": Title(value=""),
        },
        title="",
        id="d18e78e482e94a3995c18e1932ae9fb8",
        url="https://www.notion.so/d18e78e482e94a3995c18e1932ae9fb8",
    )
    expected1 = Page(
        parent_id="19ef8e6eab3542aa91a2f4aa54623479",
        properties={
            "p_url": URL(value="https://developers.notion.com/reference/property-object"),
            "p_select": Select(value="topic1"),
            "p_number": Number(value=1),
            "p_relation": Relation(
                value=[
                    "633144dd78bf4fe6800e83a530c3d87e",
                    "eda17f339aa24341b6ab07bdf0e55b24",
                    "3f4ce0fddde24c8fb3012905170c2034",
                ]
            ),
            "p_multi_select": MultiSelect(value=["tag1", "tag2"]),
            "p_rich_text": RichText(value="This is a rich text property"),
            "p_title": Title(value="Item1"),
        },
        title="Item1",
        id="48cb3c1ee9664680884dd7bfa05913a3",
        url="https://www.notion.so/Item1-48cb3c1ee9664680884dd7bfa05913a3",
    )
    page0 = Page.from_dict(client.retrieve_page(page_id0).json())
    page1 = Page.from_dict(client.retrieve_page(page_id1).json())
    assert page0 == expected0
    assert page1 == expected1


def test_update_page():
    page0 = Page.from_dict(client.retrieve_page(page_id0).json())
    page0.properties["p_title"] = Title(value="New title")

    new_page0 = Page.from_dict(client.update_page(page0.id, page0.properties_to_dict()).json())
    assert new_page0.properties["p_title"] == Title(value="New title")

    new_page0.properties["p_title"] = Title()
    old_page0 = Page.from_dict(
        client.update_page(new_page0.id, new_page0.properties_to_dict()).json()
    )
    assert old_page0.properties["p_title"] == Title()


def test_create_archive_restore_page():
    new_page0 = Page.from_dict(client.create_page(parent_id).json())
    old_page0 = Page.from_dict(client.retrieve_page(page_id0).json())
    assert new_page0.properties == old_page0.properties

    archived_page0 = Page.from_dict(client.archive_page(new_page0.id).json())
    assert archived_page0 == new_page0

    restored_page0 = Page.from_dict(client.restore_page(archived_page0.id).json())
    assert restored_page0 == archived_page0

    client.archive_page(restored_page0.id)
