from tinydb import Query, TinyDB
from tinydb.storages import MemoryStorage

from hpm.services.notion.client import Notion
from hpm.services.notion.objects.database import Database
from hpm.services.notion.objects.page import Page
from hpm.services.notion.objects.page_properties import ALL_PAGE_PROPERTIES


def test_empty_page():
    page = Page()

    assert page.as_dict() == {
        "id": None,
        "url": None,
        "parent_id": None,
        "properties": {},
    }

    cache = TinyDB(storage=MemoryStorage)
    cache.insert(page.as_dict())
    cached_page = Page.from_cache(cache.get(Query().id == page.id))

    assert cached_page.as_dict() == page.as_dict()


def test_create_template():
    client = Notion("secret_t8bapElugK3qKYqQhlub2N0eIwfKw4K69uqCBkhkD4A")
    # Create template according to the database
    database_id = "1261444c50e4808e83cde7c2fe05ded8"

    response = client.retrieve_database(database_id)
    template = Page(
        properties={
            k: ALL_PAGE_PROPERTIES[v["type"]]()
            for k, v in response["properties"].items()
            if v["type"] in ALL_PAGE_PROPERTIES
        }
    )
    print(template)


def test_database():
    client = Notion("secret_t8bapElugK3qKYqQhlub2N0eIwfKw4K69uqCBkhkD4A")
    response = client.retrieve_database("1261444c50e4808e83cde7c2fe05ded8")
    Database.from_response(response)
