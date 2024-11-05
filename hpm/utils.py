from rich.console import Console

from .styles import theme

c = Console(theme=theme, width=80, soft_wrap=True)


def print(*args, **kwargs):
    c.print(*args, **kwargs, overflow="ellipsis")
