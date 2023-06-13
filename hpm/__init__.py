from pathlib import Path

import typer

__app_name__ = "HEP Paper Manager"
__app_version__ = "0.1.0"

APP_DIR = Path(typer.get_app_dir("hpm", force_posix=True))
APP_DIR.mkdir(parents=True, exist_ok=True)

TEMPLATE_DIR = APP_DIR / "templates"
TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)

CACHE_DIR = Path.home() / ".cache" / "hpm"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
