import json
from collections import OrderedDict
from dataclasses import dataclass

import requests

from hpm import CACHE_DIR

INSPIRE_CACHED_DIR = CACHE_DIR / "Inspire"
INSPIRE_CACHED_DIR.mkdir(parents=True, exist_ok=True)
cached_paper_ids = [p.stem for p in INSPIRE_CACHED_DIR.glob("*.json")]


@dataclass
class Paper:
    arxiv_id: str
    title: str
    authors: list[str]
    journal: str
    citations: int
    abstract: str
    url: str
    bibtex: str
    source: str

    @classmethod
    def from_dict(cls, contents: dict):
        metadata = contents["metadata"]
        title = metadata["titles"][-1]["title"]

        authors = []
        if "collaborations" in metadata:
            authors.append(f"{metadata['collaborations'][0]['value']} Collaboration")
        else:
            for author in metadata["authors"][:10]:  # Only get first 10 authors
                author_name = " ".join(author["full_name"].split(", ")[::-1])
                authors.append(author_name)

        match metadata["document_type"][0]:
            case "article":
                try:
                    journal = metadata["publication_info"][0]["journal_title"]
                except KeyError:
                    journal = "Unpublished"
            case "conference paper":
                for i in metadata["publication_info"]:
                    if "cnum" in i:
                        conf_url = i["conference_record"]["$ref"]
                        conf_contents = requests.get(conf_url).json()
                        conf_metadata = conf_contents["metadata"]
                        if "acronyms" in conf_metadata:
                            journal = conf_metadata["acronyms"][0]
                        else:
                            journal = conf_metadata["titles"][0]["title"]
                        break

        citations = metadata["citation_count"]
        abstract = metadata["abstracts"][-1]["value"]
        url = f"https://inspirehep.net/literature/{metadata['control_number']}"

        bibtex_link = contents["links"]["bibtex"]
        bibtex_response = requests.get(bibtex_link)
        bibtex = bibtex_response.text[:-1]

        return Paper(
            arxiv_id=contents["id"],
            title=title,
            authors=authors,
            journal=journal,
            citations=citations,
            abstract=abstract,
            url=url,
            bibtex=bibtex,
            source="Inspire",
        )


class Inspire:
    def __init__(self):
        self.api = "https://inspirehep.net/api/arxiv/"

    def get(self, arxiv_id: str) -> Paper:
        if arxiv_id in cached_paper_ids:
            print("Fetching from cache...")
            with open(INSPIRE_CACHED_DIR / f"{arxiv_id}.json", "r") as f:
                contents = json.load(f)
            paper = Paper.from_dict(contents)

        else:
            print("Fetching from InspireHEP...")
            url = self.api + arxiv_id
            response = requests.get(url)

            if response.status_code != 200:
                log_file = CACHE_DIR / f"{arxiv_id}.log"
                with open(log_file, "w") as f:
                    f.writelines(response.text)
                raise Exception(f"Error fetching the paper, check {log_file.absolute()}")

            contents = response.json(object_pairs_hook=OrderedDict)
            paper = Paper.from_dict(contents)

            if paper.journal != "Unpublished":
                print(f"Caching the new paper {arxiv_id}...")
                with open(INSPIRE_CACHED_DIR / f"{arxiv_id}.json", "w") as f:
                    json.dump(response.json(), f, indent=4)

        return paper
