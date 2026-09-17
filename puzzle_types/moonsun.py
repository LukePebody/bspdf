from .common import moonsun as decode
ENGLISH_NAME = "Moon or Sun"
RENDERER = "region"
RULES = (
    "Draw one non-crossing loop that visits every room exactly once.",
    "In each room it uses all moons and no suns, or all suns and no moons; consecutive rooms cannot use the same symbol type.",
)
