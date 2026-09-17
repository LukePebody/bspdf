from .common import numbers as decode
ENGLISH_NAME = "Nurikabe"
RENDERER = "nurikabe"
RULES = (
    "Shade cells so each unshaded island contains exactly one clue and has the indicated size.",
    "All shaded cells connect orthogonally, and no 2x2 area may be entirely shaded.",
)
