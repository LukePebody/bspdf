from .common import pipelink as decode
ENGLISH_NAME = "Pipelink"
RENDERER = "pipelink"
RULES = (
    "Draw one loop through every cell, extending every given segment without adding another segment in that cell.",
    "The loop may cross itself only as two straight segments; it cannot branch or otherwise overlap.",
)
