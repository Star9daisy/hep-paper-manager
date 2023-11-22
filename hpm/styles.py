from rich.theme import Theme

theme = Theme(
    {
        "sect": "white",  # section
        "info": "blue",  # informatiom
        "done": "green",  # done
        "ques": "yellow",  # question
        "error": "red",  # error
        "warn": "yellow",  # warning
        "hint": "italic yellow",  # hint
        "path": "cyan underline",  # path
        "number": "cyan",  # number
    },
    inherit=False,
)
