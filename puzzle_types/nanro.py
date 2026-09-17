from .common import regions as decode
ENGLISH_NAME = "Nanro"
RENDERER = "region"
RULES = (
    "Enter numbers so every room has at least one, and each number equals the count of numbered cells in its room.",
    "Equal numbers in different rooms cannot touch; numbered cells form one connected area and no filled 2x2.",
)
