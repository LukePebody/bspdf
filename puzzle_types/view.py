from .common import number10 as decode
ENGLISH_NAME = "View"
RENDERER = "nurikabe"
RULES = (
    "Place numbers in some cells so each equals the total empty cells visible horizontally and vertically from it.",
    "Equal numbers cannot touch orthogonally, and all numbered cells form one connected area.",
)
