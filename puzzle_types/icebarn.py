from .common import icebarn as decode
ENGLISH_NAME = "Ice Barn"
RENDERER = "icebarn"
RULES = (
    "Draw one path from IN to OUT, following every arrow in its direction and visiting every connected ice area.",
    "The path cannot branch or overlap, cannot turn on ice, and may cross itself only on ice.",
)
