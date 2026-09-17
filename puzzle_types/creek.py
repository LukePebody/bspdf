from .common import creek as decode
ENGLISH_NAME = "Creek"
RENDERER = "creek"
RULES = (
    "Shade cells; each intersection clue counts the shaded cells among the up to four cells touching it.",
    "All unshaded cells must form one orthogonally connected area.",
)
