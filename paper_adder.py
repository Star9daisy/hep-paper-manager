import json

import requests
from rich import print

from utils import Paper, to_property, to_relation
import typer


def main(corpus_id: str, source: str = "remote"):
    # interface
    # ---------------------------------------------------------------------------- #
    paper = Paper()

    # semantic engine
    # ---------------------------------------------------------------------------- #
    semantic_url = "https://api.semanticscholar.org/graph/v1/paper"
    fields = "externalIds,title,tldr,url"
    semantic_url = f"{semantic_url}/CorpusID:{corpus_id}?fields={fields}"
    semantic_response = requests.get(semantic_url)
    semantic_content = json.loads(semantic_response.text)

    # update paper info
    paper.title = semantic_content["title"]
    if semantic_content["tldr"]:
        paper.tldr = semantic_content["tldr"]["text"]
    paper.corpus_id = str(semantic_content["externalIds"].get("CorpusId"))
    paper.arxiv_id = semantic_content["externalIds"].get("ArXiv")
    paper.semantic_link = semantic_content["url"]

    # inspire engine
    # ---------------------------------------------------------------------------- #
    inspire_url = "https://inspirehep.net/api"
    inspire_url = f"{inspire_url}/arxiv/{paper.arxiv_id}"
    inspire_response = requests.get(inspire_url)
    inspire_content = json.loads(inspire_response.text).get("metadata")

    # update paper info
    paper.title = inspire_content["titles"][0]["title"]
    if "collaborations" in inspire_content:
        paper.authors = [inspire_content["collaborations"][0]["value"] + " Collaboration"]
    else:
        paper.authors = [i["ids"][0]["value"][:-2] for i in inspire_content["authors"][:10]]
    if "publication_info" in inspire_content:
        paper.journal = inspire_content["publication_info"][0].get("journal_title", "Conference")
    paper.citations = inspire_content["citation_count"]
    paper.inspire_id = str(inspire_content["control_number"])
    paper.inspire_link = f"https://inspirehep.net/literature/{paper.inspire_id}"

    # notion
    # ---------------------------------------------------------------------------- #
    paper_library_database_id = "0a03b33cb0c54436bcc3cdba6500c1a3"
    professors_database_id = "320a2bf0760340f3889806f8b4910481"
    token = "secret_wXJ2PM5Ff2xAx6vpoxTMGOBfiCzjraD3Oco0qhzuMcY"

    properties = {
        # base info
        "Title": to_property("title", paper.title),
        "Authors": to_relation(paper.authors, professors_database_id, token, source),
        # "TLDR": to_property("rich_text", paper.tldr),
        "Journal": to_property("select", paper.journal),
        "Citations": to_property("number", paper.citations),
        # identification
        "Corpus ID": to_property("rich_text", paper.corpus_id),
        "Arxiv ID": to_property("rich_text", paper.arxiv_id),
        "Inspire ID": to_property("rich_text", paper.inspire_id),
        # related links
        "Semantic Link": to_property("url", paper.semantic_link),
        "Inspire Link": to_property("url", paper.inspire_link),
        # "Github Link": to_property("url", paper.github_link),
        # to be decided by the user
        "Status": to_property("status", paper.status),
        "Type": to_property("select", paper.type),
        "Field": to_property("select", paper.field),
        # "Method Type": get_property("select", self.method_type),
        # "Method Name": get_property("select", self.method_name),
        # "Task": get_property("select", self.task),
        "Update": to_property("select", paper.update),
    }

    notion_url = "https://api.notion.com/v1/pages"
    payload = {
        "parent": {
            "type": "database_id",
            "database_id": paper_library_database_id,
        },
        "properties": properties,
    }
    headers = {
        "accept": "application/json",
        "Notion-Version": "2022-06-28",
        "content-type": "application/json",
        "authorization": f"Bearer {token}",
    }

    notion_response = requests.post(notion_url, json=payload, headers=headers)

    match notion_response.status_code:
        case 200:
            print(f"✓ Succesfully added paper {paper.corpus_id}")
            print(paper)
        case _:
            print(f"✘ Something wrong with paper {paper.corpus_id}")
            print(notion_response.text)


if __name__ == "__main__":
    typer.run(main)
