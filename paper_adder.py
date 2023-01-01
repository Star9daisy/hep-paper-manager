import typer
from rich import print
from utils import search_in_semantic, search_in_inspire, add_to_notion


# test data
# 251018640: no publication_info
# 246652443: publication_info has no journal_title
# 254591719: conference paper
# 67855972: regular paper

app = typer.Typer()


@app.command()
def main(corpus_id: str, topic: str = "Unknown"):
    print(f"> Search paper {corpus_id} in Semantic Scholar...")
    semantic_paper = search_in_semantic(corpus_id)
    print(semantic_paper)

    print(f"> Search paper {semantic_paper.arxiv_id} in Inpsire HEP...")
    inspire_paper = search_in_inspire(semantic_paper.arxiv_id)
    inspire_paper.corpus_id = semantic_paper.corpus_id
    inspire_paper.arxiv_id = semantic_paper.arxiv_id
    inspire_paper.semantic_link = semantic_paper.semantic_link
    print(inspire_paper)

    print(f"> Add paper to Notion...")
    add_to_notion(inspire_paper, topic)


if __name__ == "__main__":
    app()
