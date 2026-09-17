from .common import regions as decode
ENGLISH_NAME = "LITS"
RENDERER = "region"
RULES = (
    "Shade one tetromino in every room so all shaded cells form one connected area with no shaded 2x2 square.",
    "Identical tetrominoes may not share an edge, counting rotations and reflections as the same.",
)
