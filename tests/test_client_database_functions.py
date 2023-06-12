import os

from dotenv import load_dotenv

from hpm.notion import Client
from hpm.notion.objects import Database, Page
from hpm.notion.properties import *

load_dotenv(".env")
token = os.getenv("TOKEN")
client = Client(token)
parent_id = "19ef8e6eab3542aa91a2f4aa54623479"


def test_retrieve_and_query_database():
    expected = Database(
        id="19ef8e6eab3542aa91a2f4aa54623479",
        title="Test General Database",
        description="Contains two pages: one with all properties and the other is a blank page",
        url="https://www.notion.so/19ef8e6eab3542aa91a2f4aa54623479",
        properties={
            "p_url": DatabaseURL(value=""),
            "p_select": DatabaseSelect(value=["topic1"]),
            "p_number": DatabaseNumber(value="number"),
            "p_relation": DatabaseRelation(value="480d39ea2a6d49d3a6e9af7b2aed8152"),
            "p_multi_select": DatabaseMultiSelect(value=["tag1", "tag2"]),
            "p_rich_text": DatabaseRichText(value=""),
            "p_title": DatabaseTitle(value=""),
        },
        pages=[
            Page(
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
                id="48cb3c1ee9664680884dd7bfa05913a3",
                url="https://www.notion.so/Item1-48cb3c1ee9664680884dd7bfa05913a3",
            ),
            Page(
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
                id="d18e78e482e94a3995c18e1932ae9fb8",
                url="https://www.notion.so/d18e78e482e94a3995c18e1932ae9fb8",
            ),
        ],
    )

    retrieved_json = client.retrieve_database(parent_id).json()
    queried_json = client.query_database(parent_id).json()
    database = Database.from_dict(retrieved_json, queried_json)
    assert database == expected
