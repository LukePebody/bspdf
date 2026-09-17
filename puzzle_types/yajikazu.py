from .common import yajikazu as decode
ENGLISH_NAME = "Yajikazu"
RENDERER = "firefly"
RULES = (
    "Shade cells so no two shaded cells touch orthogonally and all unshaded cells stay connected.",
    "An unshaded arrow clue counts shaded cells in its direction; a shaded clue may be true or false.",
)
