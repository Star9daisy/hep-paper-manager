from time import perf_counter
import rich

from engines.inspire import get_paper_by_arxiv_id
from engines.semantic import get_paper_by_corpus_id
from notion.database import retrieve_database
from notion.page import create_page
from notion.types import URL, Number, Relation, RichText, Select, Title
from hpm.papers import InspirePaper, NotionPaper, SemanticPaper
from hpm.utils import find_relation_ids


# ---------------------------------------------------------------------------- #
corpus_id = "252683473"
token = "secret_wXJ2PM5Ff2xAx6vpoxTMGOBfiCzjraD3Oco0qhzuMcY"
papers_db = "16a0e94107334f06a08f87369ec734e9"

# From the Papers database created online, Authors are a relation property.
# Retrieve the Papers database, we can get the related database id.
response = retrieve_database(token, papers_db)
related_db_id = response.json()["properties"]["Authors"]["relation"]["database_id"]

# First send a request to semantic scholar to get the paper by corpus id.
print("Requesting Semantic Scholar...", end="", flush=True)
_start = perf_counter()
sem_paper = SemanticPaper.from_response(get_paper_by_corpus_id(corpus_id))
_end = perf_counter()
print(f"OK in {_end-_start:.2f}s")

# Second send a request to inspire to get the paper by arxiv id.
print("Requesting Inspire...", end="", flush=True)
_start = perf_counter()
ins_paper = InspirePaper.from_response(get_paper_by_arxiv_id(sem_paper.arxiv_id))
_end = perf_counter()
print(f"OK in {_end-_start:.2f}s")

# Transform the authors to relation ids.
print("Finding authors...", end="", flush=True)
_start = perf_counter()
authors = ins_paper.authors
ids = find_relation_ids(token, related_db_id, authors)
_end = perf_counter()
print(f"OK in {_end-_start:.2f}s")

# Then fill the NotionPaper that represents one page in the Papers database.
# Note: You need to modify the NotionPaper class to fulfill your needs.
paper = NotionPaper(
    Title=Title(content=sem_paper.title),
    Published=Select(name=ins_paper.published),
    Authors=Relation(ids=ids),
    Citations=Number(number=ins_paper.citations),
    ArxivID=RichText(content=ins_paper.arxiv_id),
    CorpusID=RichText(content=sem_paper.corpus_id),
    SemanticURL=URL(url=sem_paper.url),
    InspireURL=URL(url=ins_paper.url),
)

# Finally, create the page in the Papers database.
print("Adding to Notion...", end="", flush=True)
_start = perf_counter()
response = create_page(
    token,
    {"type": "database_id", "database_id": papers_db},
    paper.to_properties(),
)
_end = perf_counter()
print(f"OK in {_end-_start:.2f}s")

if response.status_code == 200:
    rich.print(paper)
else:
    rich.print(response.text)
