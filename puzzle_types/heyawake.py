from .common import room_regions as decode
ENGLISH_NAME = "Heyawake"
RENDERER = "region"
RULES = (
    "Shade cells so no two shaded cells touch orthogonally and all unshaded cells stay connected.",
    "A room's number is its shaded-cell count; no straight unshaded run may cross two room borders.",
)
