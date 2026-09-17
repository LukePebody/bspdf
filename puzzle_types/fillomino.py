from .common import numbers as decode
ENGLISH_NAME = "Fillomino"
RENDERER = "nurikabe"
RULES = (
    "Divide the grid into regions; every clue equals the size of its region.",
    "A region may contain repeated equal clues or no clue, but equal-sized regions cannot share an edge.",
)
