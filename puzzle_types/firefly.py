from .common import firefly as decode
ENGLISH_NAME = "Hotaru Beam"
RENDERER = "firefly"
RULES = (
    "Draw non-branching, non-crossing paths from the fireflies so all paths form one connected network.",
    "A path cannot directly join two black dots; a number gives the turns made before reaching another firefly.",
)
