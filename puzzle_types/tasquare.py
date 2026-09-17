from .common import number16 as decode
ENGLISH_NAME = "Tasquare"
RENDERER = "nurikabe"
RULES = (
    "Shade filled square blocks, keeping all clue cells white and all unshaded cells connected.",
    "A clue is the total area of blocks touching it orthogonally; a blank clue must touch at least one block.",
)
