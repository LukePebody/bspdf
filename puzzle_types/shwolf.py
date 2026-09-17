from .common import shwolf as decode
ENGLISH_NAME = "Sheep and Wolves"
RENDERER = "shwolf"
RULES = (
    "Draw borders to make cages, each holding at least one animal and never mixing goats with wolves.",
    "Borders turn only at dots, go straight through crossings, and never dead-end; a dot has at most two incident borders and dot-cycles are forbidden.",
)
