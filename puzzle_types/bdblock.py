from .common import bdblock as decode
ENGLISH_NAME = "Border Block"
RENDERER = "bdblock"
RULES = (
    "Divide the grid into blocks: equal numbers share a block, different numbers do not, and every block has a number.",
    "Three or four borders meet exactly at the marked dots; borders cannot branch, cross elsewhere, or dead-end.",
)
