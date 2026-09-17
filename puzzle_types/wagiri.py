from .common import wagiri as decode
ENGLISH_NAME = "Wagiri"
RENDERER = "wagiri"
RULES = (
    "Draw one diagonal in every cell; an intersection clue counts the diagonals meeting there.",
    "A cell marked Ring must lie on a diagonal loop, while a cell marked Cut must not.",
)
