import requests
from requests import Response


# ---------------------------------------------------------------------------- #
def get_paper_by_arxiv_id(arxiv_id: str) -> Response:
    api = "https://inspirehep.net/api"
    url = f"{api}/arxiv/{arxiv_id}"

    return requests.get(url)
