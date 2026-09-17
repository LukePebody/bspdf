from .common import number10 as decode
ENGLISH_NAME = "Sukoro"
RENDERER = "nurikabe"
RULES = (
    "Place numbers 1-4 in some cells so each number equals the count of orthogonally adjacent numbered cells.",
    "Equal numbers cannot touch orthogonally, and all numbered cells form one connected area.",
)
