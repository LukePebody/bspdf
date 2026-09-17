from .common import number16 as decode
ENGLISH_NAME = "Kurotto"
RENDERER = "nurikabe"
RULES = (
    "Shade cells, leaving every circled cell unshaded.",
    "A circled number equals the combined size of all shaded groups touching that circle orthogonally.",
)
