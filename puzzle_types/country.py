from .common import room_regions as decode
ENGLISH_NAME = "Country Road"
RENDERER = "region"
RULES = (
    "Draw one non-crossing loop through cells, visiting every outlined country exactly once.",
    "A clue gives the number of visited cells in its country; cells on opposite sides of a border cannot both be unused.",
)
