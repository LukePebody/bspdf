from .common import room_numbers as decode
ENGLISH_NAME = "Cocktail Lamp"
RENDERER = "region"
RULES = (
    "Shade at most one connected block in each room; a clue gives its block's size.",
    "Blocks cannot touch orthogonally across room borders, cannot make a 2x2 shaded square, and must all connect diagonally.",
)
