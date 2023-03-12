from __future__ import annotations
import requests
from requests import Response


# ---------------------------------------------------------------------------- #
def get_paper_by_corpus_id(
    corpus_id: str,
    fields: str | None = "title,authors,citationCount,journal,externalIds,url",
) -> Response:
    api = "https://api.semanticscholar.org/graph/v1/paper"
    if fields:
        url = f"{api}/CorpusID:{corpus_id}?fields={fields}"
    else:
        url = f"{api}/CorpusID:{corpus_id}"

    return requests.get(url)
