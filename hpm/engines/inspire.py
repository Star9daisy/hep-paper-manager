from collections import OrderedDict
import json

import requests

from hpm import CACHE_DIR
from dataclasses import dataclass


@dataclass
class Paper:
    arxiv_id: str
    title: str
    authors: list[str]
    journal: str
    citations: int
    abstract: str

    @classmethod
    def from_json(cls, filepath: str):
        with open(filepath, "r") as f:
            contents = json.load(f)
        return cls(
            arxiv_id=contents["arxiv_id"],
            title=contents["title"],
            authors=contents["authors"],
            journal=contents["journal"],
            citations=contents["citations"],
            abstract=contents["abstract"],
        )

    @classmethod
    def from_response(cls, response: requests.Response):
        contents = response.json(object_pairs_hook=OrderedDict)

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
        return Paper(
            arxiv_id=contents["id"],
            title=title,
            authors=authors,
            journal=journal,
            citations=citations,
            abstract=abstract,
        )


class Inspire:
    def __init__(self):
        self.api = "https://inspirehep.net/api/arxiv/"

    def get(self, arxiv_id: str) -> Paper:
        url = self.api + arxiv_id
        response = requests.get(url)

        if response.status_code != 200:
            log_file = CACHE_DIR / f"{arxiv_id}.log"
            with open(log_file, "w") as f:
                f.writelines(response.text)
            raise Exception(f"Error fetching the paper, check {log_file.absolute()}")
        else:
            return Paper.from_response(response)
