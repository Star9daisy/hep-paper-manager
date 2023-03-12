import json
from dataclasses import dataclass, field

import requests

# ---------------------------------------------------------------------------- #
@dataclass
class Paper:
    title: str = ""
    authors: list[str] = field(default_factory=list)
    published: str = ""
    citations: int = 0

    corpus_id: str = ""
    arxiv_id: str = ""
    semantic_link: str = ""
    inspire_link: str = ""

    bibtex: str = ""


def search_in_semantic(corpus_id: str):
    api = "https://api.semanticscholar.org/graph/v1/paper"
    fields = "title,authors,citationCount,journal,externalIds,url"
    url = f"{api}/CorpusID:{corpus_id}?fields={fields}"
    response = requests.get(url)
    if response.status_code != 200:
        print(response.text)
        raise LookupError(f"✘ Something wrong with paper {corpus_id}")

    # ------------------------------------------------------------------------ #
    metadata = json.loads(response.text)
    # with open(f"semantic_{corpus_id}.json", "w") as f:
    #     json.dump(metadata, f, indent=4)

    paper = Paper()
    paper.title = metadata["title"]
    paper.authors = [author["name"] for author in metadata["authors"][:10]]
    paper.published = metadata["journal"]["name"] if metadata["journal"] else "Unpublished"
    paper.citations = metadata["citationCount"]
    paper.corpus_id = corpus_id
    paper.arxiv_id = metadata["externalIds"].get("ArXiv", "")
    paper.semantic_link = metadata["url"]

    return paper


def search_in_inspire(arxiv_id: str):
    api = "https://inspirehep.net/api"
    url = f"{api}/arxiv/{arxiv_id}"
    response = requests.get(url)
    if response.status_code != 200:
        print(response.text)
        raise LookupError(f"✘ Something wrong with paper {arxiv_id}")

    # ------------------------------------------------------------------------ #
    content = json.loads(response.text)
    bibtex_url = content["links"]["bibtex"]
    metadata = content["metadata"]
    # with open(f"inspire_{arxiv_id}.json", "w") as f:
    #     json.dump(metadata, f, indent=4)

    paper = Paper()
    paper.title = metadata["titles"][0]["title"]
    # author
    if "collaborations" in metadata:
        paper.authors = [metadata["collaborations"][0]["value"] + " Collaboration"]
    else:
        for author in metadata["authors"][:10]:
            for i in author["ids"]:
                if i["schema"] == "INSPIRE BAI":
                    paper.authors.append(i["value"][:-2])
    # journal or conference
    if metadata["document_type"][0] == "article":
        paper.published = metadata.get("publication_info", [{}])[0].get(
            "journal_title", "Unpublished"
        )
    elif metadata["document_type"][0] == "conference paper":
        if "publication_info" in metadata:
            for i in metadata["publication_info"]:
                if "cnum" in i:
                    conference_url = i["conference_record"]["$ref"]
                    conference_response = requests.get(conference_url)
                    paper.published = json.loads(conference_response.text)["metadata"]["acronyms"][0]
        else:
            paper.published = "Unpublished"
    else:
        paper.published = "Unpublished"
    # citations
    paper.citations = metadata["citation_count"]
    # link
    paper.inspire_link = f"https://inspirehep.net/literature/{metadata['control_number']}"
    # bibtex
    bibtex_response = requests.get(bibtex_url)
    paper.bibtex = bibtex_response.text[:-1]  # remove the final \n

    return paper


def query_a_database(database_id, token):
    url = f"https://api.notion.com/v1/databases/{database_id}/query"

    payload = {"page_size": 100}
    headers = {
        "accept": "application/json",
        "Notion-Version": "2022-06-28",
        "content-type": "application/json",
        "authorization": f"Bearer {token}",
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 200:
        print(response.text)
        raise LookupError(f"✘ Something wrong")

    # ------------------------------------------------------------------------ #
    database = json.loads(response.text)
    # with open(f"database_{database_id}.json", "w") as f:
    #     json.dump(database, f, indent=4)

    return database


def create_a_page(properties, database_id, token):
    url = "https://api.notion.com/v1/pages"
    payload = {
        "parent": {
            "type": "database_id",
            "database_id": database_id,
        },
        "properties": properties,
    }
    headers = {
        "accept": "application/json",
        "Notion-Version": "2022-06-28",
        "content-type": "application/json",
        "authorization": f"Bearer {token}",
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        print(f"✓ Succesfully created in {database_id}")
    else:
        print(response.text)
        raise LookupError(f"✘ Something wrong")


def to_property(property, value, **kwargs):
    match property:
        case "title" | "rich_text":
            return {property: [{"text": {"content": value}}]}

        case "number" | "url":
            return {property: value}

        case "select" | "status":
            return {property: {"name": value}}

        case "multi_select":
            return {property: [{"name": str(i)} for i in value]}

        case "relation":
            database = query_a_database(kwargs["database_id"], kwargs["token"])
            relation = {}
            for i in database["results"]:
                _name = i["properties"]["Name"]["title"][0]["plain_text"]
                _id = i["id"]
                relation[_name] = _id
            return {property: [{"id": relation[i]} for i in value if i in relation]}


def add_to_notion(paper: Paper, topic: str = "Unknown"):
    literatures_database_id = "841535b763e249579001f81df2a72369"
    professors_database_id = "70c49e69591c4cae8dee77c55b5237b2"
    token = "secret_wXJ2PM5Ff2xAx6vpoxTMGOBfiCzjraD3Oco0qhzuMcY"

    properties = {
        "Title": to_property("title", paper.title),
        "Authors": to_property(
            "relation",
            paper.authors,
            database_id=professors_database_id,
            token=token,
        ),
        "Citations": to_property("number", paper.citations),
        "Published": to_property("select", paper.published),
        "Topic": to_property("select", topic),
        "Corpus ID": to_property("rich_text", paper.corpus_id),
        "Arxiv ID": to_property("rich_text", paper.arxiv_id),
        "Semantic Link": to_property("url", paper.semantic_link),
        "Inspire Link": to_property("url", paper.inspire_link),
        "Bibtex": to_property("rich_text", paper.bibtex),
    }

    create_a_page(properties, literatures_database_id, token)


# find page ids for names
def find_relation_ids(token, database_id, names):
    database = query_a_database(
        token=token,
        database_id=database_id,
    )

    ids = []
    for result in database["results"]:
        _id = result["id"]
        _title = ""
        for content in result["properties"].values():
            if content["type"] == "title":
                _title = content["title"][0]["text"]["content"]
                break
        if _title in names:
            ids.append(_id)
    return ids
