from rich.theme import Theme

theme = Theme(
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
