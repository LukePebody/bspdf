from .common import number16 as decode
ENGLISH_NAME = "Kurodoko"
RENDERER = "nurikabe"
RULES = (
    "Shade cells so shaded cells never touch orthogonally and all unshaded cells stay connected.",
    "Clues remain unshaded and count all visible unshaded cells horizontally and vertically, including themselves.",
)
