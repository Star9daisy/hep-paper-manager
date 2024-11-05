import pytest

from hpm.services.inspire_hep.client import InspireHEP


@pytest.fixture
def client():
    return InspireHEP()


def test_get_author_by_id(client):
    client.get_author("1614261")


def test_get_paper_by_id(client):
    client.get_paper("1405106")


def test_get_paper_by_arxiv_id(client):
    client.get_paper("1511.05190")


def test_get_job_by_id(client):
    client.get_job("2832881")
