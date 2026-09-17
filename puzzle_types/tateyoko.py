from .common import tateyoko as decode
ENGLISH_NAME = "Tateyoko"
RENDERER = "tateyoko"
RULES = (
    "Draw a horizontal or vertical bar through every white cell.",
    "A white clue gives its bar's length and each bar has at most one clue; a black clue counts bars ending at that cell.",
)
