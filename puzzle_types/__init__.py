"""Puzzle-type plug-ins.

Each supported puzz.link problem type lives in its own module.  A module exposes
an English display name, a decoder, and the key of the renderer it uses.
"""

from importlib import import_module


def get_type_module(puzzle_type):
    """Return the module for *puzzle_type*, or ``None`` when unsupported."""
    module_name = puzzle_type.replace("-", "_")
    qualified_name = f"{__name__}.{module_name}"
    try:
        return import_module(f".{module_name}", __name__)
    except ModuleNotFoundError as exc:
        if exc.name == qualified_name:
            return None
        raise


def supported_types():
    """Return the puzzle types currently supported by the application."""
    return (
        "akari", "ayeheya", "bag", "barns", "bdblock", "cbblock",
        "chainedb", "cocktail", "country", "creek", "dbchoco", "factors",
        "fillomino", "firefly", "fivecells", "gokigen", "hashi", "hebi",
        "heyawake", "hitori", "icebarn", "icelom", "icelom2", "kakuro",
        "kinkonkan", "koburin", "kuroclone", "kurodoko", "kurotto",
        "lightup", "lits", "mashu", "midloop", "mochikoro", "moonsun",
        "nanro", "norinori", "numlin", "nuribou", "nurikabe", "nurimaze",
        "pipelink", "reflect", "ringring", "sashigane", "shakashaka",
        "shikaku", "shimaguni", "shugaku", "shwolf", "simpleloop",
        "slalom", "slither", "starbattle", "sukoro", "tapa", "tasquare",
        "tateyoko", "usoone", "view", "wagiri", "yajikazu",
        "yajilin-regions", "yajirin",
    )
