from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
from datetime import datetime

import requests


class Inspire:
    def __init__(self):
        self.api = "https://inspirehep.net/api/"

    def get(self, identifier_type: str, identifier_value: str):
        if identifier_type not in ["literature", "doi", "arxiv"]:
            raise ValueError("Only literature, doi, arxiv are supported for now")

        url = self.api + identifier_type + "/" + identifier_value
        response = requests.get(url)

        if response.status_code != 200:
            raise ValueError(f"Failed to get data from InspireHEP: {response.text}")

        return response.json(object_pairs_hook=OrderedDict)


@dataclass
class InspirePaper:
    date: str
    citations: int
    title: str
    type: str
    journal: str
    authors: list[str]
    link: str
    abstract: str
    bibtex: str
    inspire_id: str
    arxiv_id: str
    doi: str

    @classmethod
    def from_dict(cls, response_json: dict):
        metadata = response_json["metadata"]

        # Title
        title = metadata["titles"][0]["title"]
        if "inline\\" in title:
            title = metadata["titles"][-1]["title"]

        # Authors
        authors = []
        if "collaborations" in metadata:
            authors.append(f"{metadata['collaborations'][0]['value']} Collaboration")
        else:
            for author in metadata["authors"][:10]:  # Only get first 10 authors
                author_name = " ".join(author["full_name"].split(", ")[::-1])
                authors.append(author_name)

        # Number of citations
        n_citations = metadata["citation_count"]

        # Journal
        journal = "Unpublished"
        if metadata["document_type"][0] == "article":
            try:
                journal = metadata["publication_info"][0]["journal_title"]
            except KeyError:
                journal = "Unpublished"
        elif metadata["document_type"][0] == "conference paper":
            try:
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
            except KeyError:
                journal = "Unpublished"

        # Abstract
        abstract = metadata["abstracts"][0]["value"]
        if len(abstract) > 2000:
            abstract = abstract[:1997] + "..."

        # Bibtext
        bibtex_link = response_json["links"]["bibtex"]
        bibtex_response = requests.get(bibtex_link)
        bibtex = bibtex_response.text[:-1]

        # Inspire ID
        inspire_id = str(metadata["control_number"])

        # Arxiv ID
        arxiv_id = ""
        if "arxiv_eprints" in metadata:
            arxiv_id = metadata["arxiv_eprints"][0]["value"]

        # DOI
        doi = ""
        if "dois" in metadata:
            doi = metadata["dois"][0]["value"]

        # Date
        if "preprint_date" in metadata:
            date_str = metadata["preprint_date"]
        elif "imprints" in metadata:
            date_str = metadata["imprints"][0]["date"]
        else:
            raise ValueError("No date found")

        if date_str.count("-") > 2:
            raise ValueError(f"Unknow date format: {date_str}")
        if date_str.count("-") == 1:
            date_str += "-1"

        date = datetime.strptime(date_str, "%Y-%m-%d")
        date = date.strftime("%Y-%m-%d")

        # Type
        type = metadata["document_type"][0]
        if "publication_type" in metadata:
            pub_type = metadata["publication_type"][0]
            type = pub_type

        # Link
        link = f"https://inspirehep.net/literature/{inspire_id}"

        return cls(
            title=title,
            authors=authors,
            citations=n_citations,
            journal=journal,
            abstract=abstract,
            bibtex=bibtex,
            inspire_id=inspire_id,
            arxiv_id=arxiv_id,
            doi=doi,
            date=date,
            type=type,
            link=link,
        )
