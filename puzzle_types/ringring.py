from .common import ringring as decode
ENGLISH_NAME = "Ring Ring"
RENDERER = "nurikabe"
RULES = (
    "Fill every unshaded cell with rectangular loops; loops cannot enter shaded cells.",
    "Loops may cross, but cannot overlap or share a corner.",
)
