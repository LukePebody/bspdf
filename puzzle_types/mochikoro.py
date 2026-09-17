from .common import number16 as decode
ENGLISH_NAME = "Mochikoro"
RENDERER = "nurikabe"
RULES = (
    "Shade cells so each unshaded region is rectangular and contains at most one clue; a clue gives its area.",
    "No shaded 2x2 is allowed, and all unshaded rectangles must connect diagonally.",
)
