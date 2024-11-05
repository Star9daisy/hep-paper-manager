from tinydb import TinyDB
from tinydb.storages import MemoryStorage

from hpm.services.notion.client import Notion
from hpm.services.notion.objects.database import Database
from hpm.services.notion.objects.page import Page


def test_page():
    page = Page()

    # Test the page as a dict
    assert page.as_dict() == {"id": None, "url": None, "title": None, "properties": {}}

    # Test the page from cache
    cache = TinyDB(storage=MemoryStorage)
    cache.insert(page.as_dict())
    cached_page = Page.from_cache(cache.all()[0])

    assert page == cached_page


def test_database(TEST_DATABASE_ID):
    client = Notion()
    response = client.retrieve_database(TEST_DATABASE_ID)
    database = Database.from_response(response)

    assert database.title == "HPM Test Database"
