from .common import number16 as decode
ENGLISH_NAME = "Chained Block"
RENDERER = "nurikabe"
RULES = (
    "Shade blocks so each contains exactly one clue; a number gives that block's size.",
    "Every block touches another diagonally. Within a diagonal chain, no two block shapes may match under rotation or reflection.",
)
