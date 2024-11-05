from pathlib import Path

import typer

APP_DIR = Path(typer.get_app_dir("hpm", force_posix=True))
TOKEN_FILE = APP_DIR / "TOKEN"
TEMPLATE_FILE = APP_DIR / "paper.yml"
