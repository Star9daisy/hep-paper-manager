from rich.console import Console
from rich.theme import Theme

THEME = Theme(
    {
        "sect": "bold white",  # section
        "info": "bold cyan",  # information
        "done": "bold green",  # done
        "ques": "bold yellow",  # question
        "error": "bold red",  # error
        "error_msg": "red",  # error message
        "warn": "yellow",  # warning
        "hint": "italic yellow",  # hint
        "path": "cyan underline",  # path
        "url": "dim underline",  # url
        "num": "cyan",  # number
    },
    inherit=False,
)

console = Console(theme=THEME)


def print(*args, **kwargs):
    console.print(*args, **kwargs, overflow="ignore", crop=False)
