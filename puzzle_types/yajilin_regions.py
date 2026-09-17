from .common import room_numbers as decode
ENGLISH_NAME = "Regional Yajilin"
RENDERER = "region"
RULES = (
    "Shade cells and draw one non-crossing loop through every remaining cell.",
    "Shaded cells cannot touch orthogonally; each room clue gives the number of shaded cells in that room.",
)
