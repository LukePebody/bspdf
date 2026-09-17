from .common import room_regions as decode
ENGLISH_NAME = "Aye-Heya"
RENDERER = "region"
RULES = (
    "Shade cells so no two shaded cells touch orthogonally and all unshaded cells stay connected.",
    "A room's number is its shaded-cell count, and the shading in each room has 180-degree symmetry.",
    "No straight run of unshaded cells may cross two room borders.",
)
