from pathlib import Path

__app_name__ = "HEP Paper Manager"
__app_version__ = "0.1.0"

CACHE_DIR = Path.home() / ".cache" / "hpm"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
CACHED_PAPERS_DIR = CACHE_DIR / "cached_papers"
CACHED_AUTHORS_DIR = CACHE_DIR / "cached_authors"
