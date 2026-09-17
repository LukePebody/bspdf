from .common import usoone_regions as decode
ENGLISH_NAME = "Uso-one"
RENDERER = "region"
RULES = (
    "Shade non-clue cells so shaded cells do not touch orthogonally and all unshaded cells stay connected.",
    "A clue normally counts adjacent shaded cells, but exactly one clue in every room must be false.",
)
