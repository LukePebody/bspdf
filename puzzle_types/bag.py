from .common import numbers as decode
ENGLISH_NAME = "Bag"
RENDERER = "nurikabe"
RULES = (
    "Draw one non-branching loop on grid edges, with every clue inside the loop.",
    "A clue counts the inside cells visible from it horizontally and vertically, including its own cell.",
)
