from .common import usoone_cells as decode
ENGLISH_NAME = "Koburin"
RENDERER = "nurikabe"
RULES = (
    "Shade cells and draw one non-crossing loop through every remaining non-clue cell.",
    "Shaded cells cannot touch orthogonally; each clue counts adjacent shaded cells and cannot be shaded or used by the loop.",
)
