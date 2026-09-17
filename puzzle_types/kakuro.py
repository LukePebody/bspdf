from .common import kakuro as decode
ENGLISH_NAME = "Kakuro"
RENDERER = "kakuro"
RULES = (
    "Fill white cells with digits 1-9. Each clue is the sum of the run immediately right of or below it.",
    "A digit cannot repeat within a horizontal or vertical run.",
)
