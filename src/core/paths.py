import pathlib

CURRENT_DIR = pathlib.Path(__file__).parent.parent.resolve()

STATIC_DIR = CURRENT_DIR / "static"
MEDIA_DIR = CURRENT_DIR.parent / "media"