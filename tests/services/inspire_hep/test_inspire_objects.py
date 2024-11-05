import json

from tinydb import Query, TinyDB
from tinydb.storages import MemoryStorage

from hpm.services.inspire_hep.objects import Author, Job, Paper


def test_author():
    response = json.load(open("tests/services/inspire_hep/author-1614261.json", "r"))
    author = Author.from_response(response)
    assert author.id == "1614261"

    cache = TinyDB(storage=MemoryStorage)
    cache.insert(author.as_dict())

    cached_author = Author.from_cache(cache.get(Query().id == "1614261"))
    assert author == cached_author
    assert author.as_dict() == cached_author.as_dict()

    # This author has no preferred name
    response = json.load(open("tests/services/inspire_hep/author-2005171.json", "r"))
    author = Author.from_response(response)
    assert author.id == "2005171"


def test_paper():
    response = json.load(open("tests/services/inspire_hep/paper-1405106.json", "r"))
    paper = Paper.from_response(response)
    assert paper.id == "1405106"

    cache = TinyDB(storage=MemoryStorage)
    cache.insert(paper.as_dict())

    cached_paper = Paper.from_cache(cache.get(Query().id == "1405106"))
    assert paper == cached_paper
    assert paper.as_dict() == cached_paper.as_dict()

    # 779080 preprint_date doesn't contain the day so its created_date uses the
    # created date instead
    response = json.load(open("tests/services/inspire_hep/paper-779080.json", "r"))
    paper = Paper.from_response(response)
    assert paper.id == "779080"

    # Try with an arxiv id
    response = json.load(open("tests/services/inspire_hep/paper-1511.05190.json", "r"))
    paper = Paper.from_response(response)
    assert paper.id == "1405106"
    assert paper.eprint == "1511.05190"


def test_job():
    response = json.load(open("tests/services/inspire_hep/job-2832881.json", "r"))
    job = Job.from_response(response)
    assert job.id == "2832881"

    cache = TinyDB(storage=MemoryStorage)
    cache.insert(job.as_dict())

    cached_job = Job.from_cache(cache.get(Query().id == "2832881"))
    assert job == cached_job
    assert job.as_dict() == cached_job.as_dict()
