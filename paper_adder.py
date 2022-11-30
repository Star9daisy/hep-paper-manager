import json

import requests
from rich import print

from utils import Paper, to_property, to_relation
import typer


def main(
    corpus_id: str,
    topic: str = "Unkonwn",
    review: bool = False,
    source: str = "remote",
    dry_run: bool = False,
):
    # interface
    # ---------------------------------------------------------------------------- #
    paper = Paper()

    # semantic engine
    # ---------------------------------------------------------------------------- #
    semantic_url = "https://api.semanticscholar.org/graph/v1/paper"
    fields = "title,authors,citationCount,journal,tldr,externalIds,url"
    semantic_url = f"{semantic_url}/CorpusID:{corpus_id}?fields={fields}"
    semantic_response = requests.get(semantic_url)
    semantic_content = json.loads(semantic_response.text)

    # add paper info
    paper.title = semantic_content["title"] if not review else f"✧ {semantic_content['title']}"
    paper.authors = [i["name"] for i in semantic_content["authors"][:10]]
    paper.citations = semantic_content["citationCount"]
    if semantic_content["journal"]:
        paper.published = semantic_content["journal"]["name"]
        if paper.published == "":
            paper.published = "Unpublished"

    paper.tldr = semantic_content["tldr"]["text"] if semantic_content["tldr"] else "No tldr yet"
    paper.source = "Semantic"
    paper.topic = topic
    paper.corpus_id = str(semantic_content["externalIds"]["CorpusId"])
    paper.arxiv_id = semantic_content["externalIds"].get("ArXiv", "None")
    paper.semantic_link = semantic_content["url"]

    # inspire
    # ---------------------------------------------------------------------------- #
    inspire_url = "https://inspirehep.net/api"
    inspire_url = f"{inspire_url}/arxiv/{paper.arxiv_id}"
    inspire_response = requests.get(inspire_url)

    if inspire_response.status_code != 404:
        inspire_content = json.loads(inspire_response.text).get("metadata")

        # update paper info
        paper.title = inspire_content["titles"][0]["title"]
        paper.title = paper.title if not review else f"✧ {paper.title}"
        if "collaborations" in inspire_content:
            paper.authors = [inspire_content["collaborations"][0]["value"] + " Collaboration"]
        else:
            paper.authors = []
            for author in inspire_content["authors"][:10]:
                for i in author["ids"]:
                    if i["schema"] == "INSPIRE BAI":
                        paper.authors.append(i["value"][:-2])

        paper.citations = inspire_content["citation_count"]

        match inspire_content["document_type"][0]:
            case "article":
                if "publication_info" in inspire_content:
                    paper.published = inspire_content["publication_info"][0]["journal_title"]
                else:
                    paper.published = "Unpublished"
            case "conference paper":
                if "publication_info" in inspire_content:
                    for i in inspire_content["publication_info"]:
                        if "cnum" in i:
                            conference_url = i["conference_record"]["$ref"]
                            conference_response = requests.get(conference_url)
                            paper.published = json.loads(conference_response.text)["metadata"][
                                "acronyms"
                            ][0]
                else:
                    paper.published = "Unpublished"
            case _:
                paper.published = "Unknown"

        paper.source = "Inspire"
        paper.inspire_link = (
            f"https://inspirehep.net/literature/{inspire_content['control_number']}"
        )

        bibtex_url = f"{inspire_url}?format=bibtex"
        bibtex_response = requests.get(bibtex_url)
        paper.bibtex = bibtex_response.text[:-1]  # remove the final \n
    else:
        print(f"! Couldn't find paper {paper.corpus_id} arxiv_id on Inspire HEP")
        print(f"! Use Semantic source insead")

    if dry_run:
        print(paper)
    else:

        # notion
        # ---------------------------------------------------------------------------- #
        paper_library_database_id = "841535b763e249579001f81df2a72369"
        professors_database_id = "70c49e69591c4cae8dee77c55b5237b2"
        token = "secret_wXJ2PM5Ff2xAx6vpoxTMGOBfiCzjraD3Oco0qhzuMcY"

        properties = {
            # base info
            "Title": to_property("title", paper.title),
            "Authors": to_relation(paper.authors, professors_database_id, token, source),
            "Citations": to_property("number", paper.citations),
            "Published": to_property("select", paper.published),
            "TLDR": to_property("rich_text", paper.tldr),
            "Source": to_property("select", paper.source),
            "Topic": to_property("select", paper.topic),
            "Corpus ID": to_property("rich_text", paper.corpus_id),
            "Semantic Link": to_property("url", paper.semantic_link),
        }
        if inspire_response.status_code != 404:
            properties.update(
                {
                    "Arxiv ID": to_property("rich_text", paper.arxiv_id),
                    "Inspire Link": to_property("url", paper.inspire_link),
                    "Bibtex": to_property("rich_text", paper.bibtex),
                }
            )

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
