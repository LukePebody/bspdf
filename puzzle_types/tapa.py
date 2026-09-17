from .common import tapa as decode
ENGLISH_NAME = "Tapa"
RENDERER = "nurikabe"
RULES = (
    "Shade cells so all shading connects orthogonally and contains no 2x2 block; clue cells stay white.",
    "A clue lists the lengths of consecutive shaded runs among its eight neighbours, in any order.",
)
