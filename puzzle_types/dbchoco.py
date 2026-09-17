from .common import dbchoco as decode
ENGLISH_NAME = "Double Choco"
RENDERER = "dbchoco"
RULES = (
    "Divide the grid into regions, each containing one connected white shape and one connected grey shape.",
    "The two shapes must match in size and shape, allowing rotation or reflection; a clue gives its shape's size.",
)
