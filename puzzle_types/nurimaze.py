from .common import nurimaze as decode
ENGLISH_NAME = "Nurimaze"
RENDERER = "nurimaze"
RULES = (
    "Shade whole rooms so clues stay unshaded; neither colour may form a 2x2, and all unshaded cells form a loop-free maze.",
    "The unique S-to-G route must pass through every circle and avoid every triangle.",
)
