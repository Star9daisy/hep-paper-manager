# import typer
from rich import print
from utils import search_in_semantic, search_in_inspire, add_to_notion
import subprocess, shlex


# test data
# 251018640: no publication_info
# 246652443: publication_info has no journal_title
# 254591719: conference paper
# 67855972: regular paper

# app = typer.Typer()


# @app.command()
def main():
    corpus_id = subprocess.run(
        shlex.split("gum input --placeholder 'Enter a corpus ID'"),
        stdout=subprocess.PIPE,
        text=True,
    )
    corpus_id = corpus_id.stdout.strip()

    print(f"> Search paper {corpus_id} in Semantic Scholar...")
    semantic_paper = search_in_semantic(corpus_id)
    print(semantic_paper)
    print()

    print(f"> Search paper {semantic_paper.arxiv_id} in Inpsire HEP...")
    inspire_paper = search_in_inspire(semantic_paper.arxiv_id)
    inspire_paper.corpus_id = semantic_paper.corpus_id
    inspire_paper.arxiv_id = semantic_paper.arxiv_id
    inspire_paper.semantic_link = semantic_paper.semantic_link
    print(inspire_paper)
    print()

    print("> Choose a topic, press ctrl+c to jump over")
    topics = ' '.join([
        "Anomaly",
        "Architecture",
        "Generative",
        "Interpretability",
        "Measurement",
        "Reconstruction",
        "Tagging",
        "Observable",
        "Decorrelation",
        "Uncertainty",
        "PhaseSpace",
        "zOther",
    ])
    topic = subprocess.run(
        shlex.split(f"gum choose {topics}"),
        stdout=subprocess.PIPE,
        text=True,
    )
    topic = topic.stdout.strip()
    topic = topic if topic else "Unknown"
    print(f"> Add paper({topic}) to Notion...")
    add_to_notion(inspire_paper, topic)

while True:
    main()
    print()
    is_next = subprocess.run(
        shlex.split("gum input --placeholder 'Add another one? (press q to exit)'"),
        stdout=subprocess.PIPE,
        text=True,
    )
    if is_next.stdout.strip() == "q":
        break

# if __name__ == "__main__":
#     app()
