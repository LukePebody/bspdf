from .common import akari as decode
ENGLISH_NAME = "Akari"
RENDERER = "nurikabe"
RULES = (
    "Place lights in white cells so every white cell is illuminated horizontally or vertically.",
    "Lights cannot see one another; each black number gives the count of adjacent lights.",
)
