from .common import reflect as decode
ENGLISH_NAME = "Reflect Link"
RENDERER = "reflect"
RULES = (
    "Draw one loop; it may cross only in the marked crossing cells and cannot branch or overlap.",
    "Every triangle reflects the loop by 90 degrees; its clue totals the cells travelled on both outgoing rays before turning.",
)
