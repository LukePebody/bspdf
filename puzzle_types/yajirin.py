from .common import firefly as decode
ENGLISH_NAME = "Yajilin"
RENDERER = "firefly"
RULES = (
    "Shade cells and draw one non-crossing loop through every remaining non-clue cell.",
    "Shaded cells cannot touch orthogonally; each arrow clue counts shaded cells in its direction.",
)
