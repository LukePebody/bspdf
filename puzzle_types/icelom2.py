from .common import icelom as decode
ENGLISH_NAME = "Icelom 2"
RENDERER = "icelom"
RULES = (
    "Draw one path from IN to OUT through every number in ascending order and through every connected ice area.",
    "The path cannot branch or overlap, cannot turn on ice, and may cross itself only on ice.",
)
