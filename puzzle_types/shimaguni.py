from .common import room_regions as decode
ENGLISH_NAME = "Islands"
RENDERER = "region"
RULES = (
    "Shade one connected island in each room; a clue gives that island's size.",
    "Islands cannot connect across room borders, and neighbouring rooms must have different island sizes.",
)
