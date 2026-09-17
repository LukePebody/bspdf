from .common import icelom as decode
ENGLISH_NAME = "Icelom"
RENDERER = "icelom"
RULES = (
    "Draw one path from IN to OUT through every white cell, visiting the numbers in ascending order.",
    "The path cannot branch or overlap, cannot turn on ice, and may cross itself only on ice.",
)
