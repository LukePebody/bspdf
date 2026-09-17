from .common import fivecells as decode
ENGLISH_NAME = "Five Cells"
RENDERER = "nurikabe"
RULES = (
    "Divide the grid into regions of exactly five cells.",
    "A clue counts the borders around its cell; every drawn border must separate regions, with no dead ends.",
)
