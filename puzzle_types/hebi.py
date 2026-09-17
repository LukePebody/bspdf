from .common import firefly as decode
ENGLISH_NAME = "Hebi-Ichigo"
RENDERER = "firefly"
RULES = (
    "Place snakes made of the orthogonally connected sequence 1-2-3-4-5; snakes cannot share an edge.",
    "A snake faces away from its 2 and cannot look directly at another snake unless a black cell intervenes.",
    "A black-cell clue gives the first number seen in its arrow direction, or 0 when none is seen.",
)
