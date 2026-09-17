from .common import numbers as decode
ENGLISH_NAME = "Hitori"
RENDERER = "nurikabe"
RULES = (
    "Shade cells so no number repeats among the unshaded cells in any row or column.",
    "Shaded cells cannot touch orthogonally, and all unshaded cells must stay connected.",
)
