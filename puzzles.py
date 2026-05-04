"""Puzzle URL parser and type-specific decoders."""

from dataclasses import dataclass, field
from typing import Optional
import re

CHARS = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


@dataclass
class Puzzle:
    puzzle_type: str
    cols: int
    rows: int
    title: str = ""
    date: str = ""
    url: str = ""
    stars: int = 0


@dataclass
class NurikabePuzzle(Puzzle):
    clues: list = field(default_factory=list)  # list of (row, col, value)


@dataclass
class IceBarnPuzzle(Puzzle):
    ice: list = field(default_factory=list)       # list of (row, col)
    arrows: list = field(default_factory=list)     # list of (row, col, dr, dc, type)
    in_arrow: int = 0
    out_arrow: int = 0


@dataclass
class RegionPuzzle(Puzzle):
    """Puzzle with region borders and optional number clues (nanro, heyawake, etc.)."""
    vborders: list = field(default_factory=list)  # list of (row, col) — border right of cell
    hborders: list = field(default_factory=list)  # list of (row, col) — border below cell
    clues: list = field(default_factory=list)      # list of (row, col, value)


@dataclass
class MidloopPuzzle(Puzzle):
    """Midloop puzzle. Dots are (fine_row, fine_col) on a (2*rows-1) x (2*cols-1) fine grid.
    Even,even = cell center. Even,odd = vertical edge. Odd,even = horizontal edge."""
    dots: list = field(default_factory=list)


@dataclass
class PipelinkPuzzle(Puzzle):
    """Pipelink puzzle. Segments are (row, col, pipe_type).
    Types: 0=cross, 1=vertical, 2=horizontal, 3=bend ┘, 4=bend └, 5=bend ┐, 6=bend ┌"""
    segments: list = field(default_factory=list)  # list of (row, col, pipe_type)


@dataclass
class RegionArrowPuzzle(Puzzle):
    """Puzzle with region borders and arrow clues (kuroclone)."""
    vborders: list = field(default_factory=list)
    hborders: list = field(default_factory=list)
    clues: list = field(default_factory=list)  # list of (row, col, direction, value)


@dataclass
class FireflyPuzzle(Puzzle):
    """Hotaru Beam puzzle. Clues are (row, col, direction, value).
    Direction: 1=up, 2=down, 3=left, 4=right. Value=None means no number."""
    clues: list = field(default_factory=list)


@dataclass
class DbchocoPuzzle(Puzzle):
    """Double Choco puzzle. Grey cells + number clues."""
    grey_cells: list = field(default_factory=list)  # list of (row, col)
    clues: list = field(default_factory=list)        # list of (row, col, value)


@dataclass
class UnknownPuzzle(Puzzle):
    """Placeholder for puzzle types we haven't implemented decoders for yet."""
    pass


def parse_url(url):
    """Extract puzzle_type, cols, rows, data from a puzz.link or pzv.jp URL."""
    # Normalize URL to just the query part
    match = re.search(r'[?&]([^&]+)', url)
    if not match:
        return None, None, None, None
    query = match.group(1)
    parts = query.split("/")
    if len(parts) < 3:
        return None, None, None, None
    puzzle_type = parts[0]
    try:
        cols = int(parts[1])
        rows = int(parts[2])
    except ValueError:
        return None, None, None, None
    data = "/".join(parts[3:]) if len(parts) > 3 else ""
    return puzzle_type, cols, rows, data


def decode_nurikabe(cols, rows, data):
    """Decode nurikabe puzzle data into clue positions."""
    clues = []
    ri, ci = 0, 0
    for ch in data:
        val = CHARS.index(ch)
        if val < 16:
            clues.append((ri, ci, val))
            ci += 1
        else:
            ci += val - 15
        while ci >= cols:
            ci -= cols
            ri += 1
    return clues


def decode_icebarn(cols, rows, data_str):
    """Decode icebarn puzzle data into ice cells and arrows."""
    # data_str contains the encoded data plus /in_arrow/out_arrow at the end
    # The full query after icebarn/cols/rows/ is: encoded_data/in_arrow/out_arrow
    parts = data_str.split("/")
    code = parts[0]
    in_arrow = int(parts[1]) if len(parts) > 1 else 0
    out_arrow = int(parts[2]) if len(parts) > 2 else 0

    # Decode ice cells (bit-packed, 5 bits per character)
    ice = []
    code_index = 0
    ri, ci = 0, 0
    while ri < rows:
        k = CHARS.index(code[code_index])
        for j in range(5):
            if (k >> (4 - j)) & 1:
                ice.append((ri, ci))
            ci += 1
            if ci == cols:
                ci = 0
                ri += 1
        code_index += 1

    # Decode arrows
    arrows = []
    ri, ci, dr, dc = 0, 1, 0, -1
    first = True
    while code_index < len(code):
        k = CHARS.index(code[code_index])
        is_z = code[code_index] == 'z'
        if not (first or is_z):
            k += 1
        first = False
        code_index += 1
        skip_this_one = False
        while k > 0:
            k -= 1
            ci += 1
            if max(ci, ci + dc) == cols:
                ri += 1
                ci = 0 if dc >= 0 else 1
                if max(ri, ri + dr) == rows:
                    dr, dc = dc, -dr
                    ri = 0 if dr >= 0 else 1
                    ci = 0 if dc >= 0 else 1
                    if dr == 0:
                        skip_this_one = True
                        first = True
        if not (is_z or skip_this_one):
            arrows.append((ri, ci, dr, dc, None))

    # Add in/out arrows based on boundary position
    for arrow_val, arrow_type in [(in_arrow, "in"), (out_arrow, "out")]:
        if arrow_val < cols:
            arrows.append((-1 if arrow_type == "in" else 0, arrow_val,
                          1 if arrow_type == "in" else -1, 0, arrow_type))
        elif arrow_val < 2 * cols:
            arrows.append((rows if arrow_type == "in" else rows - 1, arrow_val - cols,
                          -1 if arrow_type == "in" else 1, 0, arrow_type))
        elif arrow_val < 2 * cols + rows:
            arrows.append((arrow_val - 2 * cols, -1 if arrow_type == "in" else 0,
                          0, 1 if arrow_type == "in" else -1, arrow_type))
        else:
            arrows.append((arrow_val - 2 * cols - rows, cols if arrow_type == "in" else cols - 1,
                          0, -1 if arrow_type == "in" else 1, arrow_type))

    return ice, arrows, in_arrow, out_arrow


def decode_ringring(cols, rows, data):
    """Decode ring ring puzzle. Base-36 char (0-9, a-z) = skip val cells then place block.
    '.' = skip 36 cells with no block. Returns list of (row, col)."""
    blocks = []
    ptr = 0
    total = rows * cols
    for ch in data:
        if ptr >= total:
            break
        if ch == '.':
            ptr += 36
            continue
        val = int(ch, 36)
        ptr += val
        if ptr < total:
            blocks.append((ptr // cols, ptr % cols))
        ptr += 1
    return blocks


def decode_midloop(cols, rows, data):
    """Decode midloop puzzle. Dots on a (2*rows-1) x (2*cols-1) fine grid.
    Odd values 1,3,...,f(15): dot, advance (val+1)/2.
    Values >= 16: skip (val-15) positions."""
    fine_cols = 2 * cols - 1
    fine_rows = 2 * rows - 1
    total = fine_rows * fine_cols
    dots = []
    ptr = 0
    for ch in data:
        if ptr >= total:
            break
        val = CHARS.index(ch)
        if val <= 15 and val % 2 == 1:  # odd values 1-15: dot
            fr = ptr // fine_cols
            fc = ptr % fine_cols
            dots.append((fr, fc))
            ptr += (val + 1) // 2
        else:  # skip
            ptr += val - 15
    return dots


def decode_pipelink(cols, rows, data):
    """Decode pipelink puzzle. a-g (10-16) = pipe types 0-6, h+ (17+) = skip (val-16)."""
    segments = []
    ptr = 0
    total = rows * cols
    for ch in data:
        if ptr >= total:
            break
        val = CHARS.index(ch)
        if val <= 16:  # a(10) through g(16) = content
            segments.append((ptr // cols, ptr % cols, val - 10))
            ptr += 1
        else:
            ptr += val - 16
    return segments


def decode_tapa(cols, rows, data):
    """Decode tapa puzzle. Single digits = 1 value. 'a'+char = 2 values (base 6).
    'b'+char = 3 values (base 4). 'c'+char = 4 values (base 3).
    Skip chars have val >= 16 after accounting for prefixes: skip = val - 15.
    Clues stored as (row, col, tuple_of_values)."""
    clues = []
    ptr = 0
    total = rows * cols
    i = 0
    while i < len(data) and ptr < total:
        ch = data[i]
        val = CHARS.index(ch)
        if ch == 'a':  # 2 values, base 6
            i += 1
            v2 = CHARS.index(data[i])
            v1, v2 = v2 // 6, v2 % 6
            # Store as string "v1/v2" for display
            clues.append((ptr // cols, ptr % cols, f"{v1}\n{v2}"))
            ptr += 1
        elif ch == 'b':  # 3 values, base 4
            i += 1
            v3 = CHARS.index(data[i])
            v1 = v3 // 16; v3 %= 16
            v2 = v3 // 4; v3 %= 4
            clues.append((ptr // cols, ptr % cols, f"{v1}\n{v2}\n{v3}"))
            ptr += 1
        elif ch == 'c':  # 4 values, base 3
            i += 1
            v4 = CHARS.index(data[i])
            v1 = v4 // 27; v4 %= 27
            v2 = v4 // 9; v4 %= 9
            v3 = v4 // 3; v4 %= 3
            clues.append((ptr // cols, ptr % cols, f"{v1}\n{v2}\n{v3}\n{v4}"))
            ptr += 1
        elif val <= 8:  # single digit value
            clues.append((ptr // cols, ptr % cols, str(val)))
            ptr += 1
        else:  # skip
            ptr += val - 15
        i += 1
    return clues


def decode_sashigane(cols, rows, data):
    """Decode sashigane puzzle. g=up, h=down, i=left, j=right arrows.
    Digits = circled numbers. '.' = empty circle. k+ = skip (val-19)."""
    clues = []
    ptr = 0
    total = rows * cols
    ARROWS = {16: 1, 17: 2, 18: 3, 19: 4}  # up, down, left, right
    for ch in data:
        if ptr >= total:
            break
        if ch == '.':
            clues.append((ptr // cols, ptr % cols, 0, None))  # empty circle
            ptr += 1
            continue
        val = CHARS.index(ch)
        if val <= 15:
            clues.append((ptr // cols, ptr % cols, 0, val))  # circled number
            ptr += 1
        elif val <= 19:
            clues.append((ptr // cols, ptr % cols, ARROWS[val], None))  # arrow
            ptr += 1
        else:
            ptr += val - 19
    return clues


def decode_firefly(cols, rows, data):
    """Decode firefly/yajilin/hebi puzzle data.
    Encoding: digit 1-4 followed by digit or '.' = arrow clue.
    '0.' = black square (direction 0, value None).
    Letters a-z = skip (CHARS.index - 9) cells. '/' = terminator.
    """
    clues = []
    ptr = 0
    total = cols * rows
    i = 0
    while i < len(data):
        if ptr >= total:
            break
        ch = data[i]
        if ch == '/':
            break
        if ch == '0' and i + 1 < len(data) and data[i + 1] == '.':
            # Black square
            clues.append((ptr // cols, ptr % cols, 0, None))
            ptr += 1
            i += 2
            continue
        if ch in '1234':
            direction = int(ch)
            i += 1
            val_ch = data[i]
            val = None if val_ch == '.' else int(val_ch)
            clues.append((ptr // cols, ptr % cols, direction, val))
            ptr += 1
        else:
            ptr += CHARS.index(ch) - 9
        i += 1
    return clues


def decode_usoone_clues(cols, rows, data, support_dot=False):
    """Decode usoone/shakashaka clue data. Different from nurikabe:
    0-4: clue value 0-4, advance 1
    5-9: clue value 0-4 (val-5), advance 2 (1 blank after)
    a-e: clue value 0-4 (val-10), advance 3 (2 blanks after)
    f-z: skip (val-15) cells
    '.': black cell with no number, advance 1 (if support_dot=True)
    """
    clues = []
    ptr = 0
    total = rows * cols
    for ch in data:
        if ptr >= total:
            break
        if ch == '.' and support_dot:
            clues.append((ptr // cols, ptr % cols, -1))  # -1 = black, no number
            ptr += 1
            continue
        val = CHARS.index(ch)
        if val <= 4:
            clues.append((ptr // cols, ptr % cols, val))
            ptr += 1
        elif val <= 9:
            clues.append((ptr // cols, ptr % cols, val - 5))
            ptr += 2
        elif val <= 14:
            clues.append((ptr // cols, ptr % cols, val - 10))
            ptr += 3
        else:
            ptr += val - 15
    return clues


def decode_regions(cols, rows, data):
    """Decode region borders + optional clues. Returns (vborders, hborders, clues, consumed).

    Encoding: first ceil(rows*(cols-1)/5) chars encode vertical borders (5 bits each),
    then ceil((rows-1)*cols/5) chars encode horizontal borders,
    then remaining chars encode clues in nurikabe style.
    """
    import math
    n_vbits = rows * (cols - 1)
    n_hbits = (rows - 1) * cols
    n_vchars = math.ceil(n_vbits / 5)
    n_hchars = math.ceil(n_hbits / 5)

    # Decode vertical borders
    vborders = []
    bits = []
    for ch in data[:n_vchars]:
        val = CHARS.index(ch)
        for bit in range(4, -1, -1):
            bits.append((val >> bit) & 1)
    for i in range(n_vbits):
        if bits[i]:
            row = i // (cols - 1)
            col = i % (cols - 1)
            vborders.append((row, col))

    # Decode horizontal borders
    bits = []
    for ch in data[n_vchars:n_vchars + n_hchars]:
        val = CHARS.index(ch)
        for bit in range(4, -1, -1):
            bits.append((val >> bit) & 1)
    hborders = []
    for i in range(n_hbits):
        if bits[i]:
            row = i // cols
            col = i % cols
            hborders.append((row, col))

    # Decode clues from remaining data
    clue_data = data[n_vchars + n_hchars:]
    clues = decode_nurikabe(cols, rows, clue_data) if clue_data else []

    return vborders, hborders, clues


def _find_rooms(cols, rows, vborders, hborders):
    """Find rooms by flood-filling from each unvisited cell. Returns rooms sorted by top-left."""
    vset = set(vborders)
    hset = set(hborders)
    visited = [[False] * cols for _ in range(rows)]
    rooms = []

    for r in range(rows):
        for c in range(cols):
            if visited[r][c]:
                continue
            queue = [(r, c)]
            visited[r][c] = True
            cells = [(r, c)]
            while queue:
                cr, cc = queue.pop(0)
                for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    nr, nc = cr + dr, cc + dc
                    if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc]:
                        # Check if there's a border between (cr,cc) and (nr,nc)
                        blocked = False
                        if dc == 1 and (cr, cc) in vset:
                            blocked = True
                        elif dc == -1 and (cr, nc) in vset:
                            blocked = True
                        elif dr == 1 and (cr, cc) in hset:
                            blocked = True
                        elif dr == -1 and (nr, nc) in hset:
                            blocked = True
                        if not blocked:
                            visited[nr][nc] = True
                            cells.append((nr, nc))
                            queue.append((nr, nc))
            rooms.append((r, c, cells))
    return rooms


def decode_regions_roomclues(cols, rows, data):
    """Decode regions with clues placed per room (heyawake style)."""
    import math as _math
    n_vchars = _math.ceil(rows * (cols - 1) / 5)
    n_hchars = _math.ceil((rows - 1) * cols / 5)

    vborders, hborders, _ = decode_regions(cols, rows, data)
    rooms = _find_rooms(cols, rows, vborders, hborders)

    clue_data = data[n_vchars + n_hchars:]
    clues = []
    ri = 0
    for ch in clue_data:
        if ri >= len(rooms):
            break
        val = CHARS.index(ch)
        if val < 16:
            r, c, cells = rooms[ri]
            clues.append((r, c, val))
            ri += 1
        else:
            ri += val - 15

    return vborders, hborders, clues


def decode_regions_usoone(cols, rows, data):
    """Like decode_regions but uses usoone clue encoding instead of nurikabe."""
    import math
    n_vbits = rows * (cols - 1)
    n_hbits = (rows - 1) * cols
    n_vchars = math.ceil(n_vbits / 5)
    n_hchars = math.ceil(n_hbits / 5)

    # Reuse border decoding from decode_regions
    vborders, hborders, _ = decode_regions(cols, rows, data)

    # Decode clues with usoone encoding
    clue_data = data[n_vchars + n_hchars:]
    clues = decode_usoone_clues(cols, rows, clue_data) if clue_data else []

    return vborders, hborders, clues


# Puzzle types that use the same "numbers in cells" encoding as nurikabe
NUMBERS_IN_CELLS_TYPES = {"nurikabe", "fillomino", "hitori", "numlin", "bag"}

# Puzzle types that use usoone-style encoding (0-4 adv 1, 5-9 adv 2, a-e adv 3, f+ skip)
USOONE_STYLE_TYPES = {"slither", "koburin"}

# Puzzle types that use the "regions + numbers" encoding
REGION_TYPES = {"nanro", "lits", "shimaguni", "country", "norinori"}

# Region types where clues are placed per room, not per cell
REGION_ROOM_CLUE_TYPES = {"heyawake", "country", "shimaguni"}


def decode_puzzle(url, title="", date=""):
    """Parse a puzz.link URL and return a Puzzle object."""
    puzzle_type, cols, rows, data = parse_url(url)
    if puzzle_type is None:
        return UnknownPuzzle(puzzle_type="unknown", cols=0, rows=0,
                            title=title, date=date, url=url)

    if puzzle_type in NUMBERS_IN_CELLS_TYPES:
        clues = decode_nurikabe(cols, rows, data)
        return NurikabePuzzle(puzzle_type=puzzle_type, cols=cols, rows=rows,
                             title=title, date=date, url=url, clues=clues)
    elif puzzle_type in REGION_ROOM_CLUE_TYPES:
        vborders, hborders, clues = decode_regions_roomclues(cols, rows, data)
        return RegionPuzzle(puzzle_type=puzzle_type, cols=cols, rows=rows,
                           title=title, date=date, url=url,
                           vborders=vborders, hborders=hborders, clues=clues)
    elif puzzle_type in REGION_TYPES:
        vborders, hborders, clues = decode_regions(cols, rows, data)
        return RegionPuzzle(puzzle_type=puzzle_type, cols=cols, rows=rows,
                           title=title, date=date, url=url,
                           vborders=vborders, hborders=hborders, clues=clues)
    elif puzzle_type == "usoone":
        vborders, hborders, clues = decode_regions_usoone(cols, rows, data)
        return RegionPuzzle(puzzle_type=puzzle_type, cols=cols, rows=rows,
                           title=title, date=date, url=url,
                           vborders=vborders, hborders=hborders, clues=clues)
    elif puzzle_type == "ringring":
        blocks = decode_ringring(cols, rows, data)
        clues = [(r, c, -1) for r, c in blocks]
        return NurikabePuzzle(puzzle_type=puzzle_type, cols=cols, rows=rows,
                             title=title, date=date, url=url, clues=clues)
    elif puzzle_type == "midloop":
        dots = decode_midloop(cols, rows, data)
        return MidloopPuzzle(puzzle_type=puzzle_type, cols=cols, rows=rows,
                            title=title, date=date, url=url, dots=dots)
    elif puzzle_type == "pipelink":
        segments = decode_pipelink(cols, rows, data)
        return PipelinkPuzzle(puzzle_type=puzzle_type, cols=cols, rows=rows,
                             title=title, date=date, url=url, segments=segments)
    elif puzzle_type == "shakashaka":
        clues = decode_usoone_clues(cols, rows, data, support_dot=True)
        return NurikabePuzzle(puzzle_type=puzzle_type, cols=cols, rows=rows,
                             title=title, date=date, url=url, clues=clues)
    elif puzzle_type == "gokigen":
        # Gokigen clues are on (cols+1) x (rows+1) intersection grid
        clues = decode_usoone_clues(cols + 1, rows + 1, data)
        return NurikabePuzzle(puzzle_type=puzzle_type, cols=cols, rows=rows,
                             title=title, date=date, url=url, clues=clues)
    elif puzzle_type in USOONE_STYLE_TYPES:
        clues = decode_usoone_clues(cols, rows, data, support_dot=True)
        return NurikabePuzzle(puzzle_type=puzzle_type, cols=cols, rows=rows,
                             title=title, date=date, url=url, clues=clues)
    elif puzzle_type == "kuroclone":
        import math as _math
        n_vchars = _math.ceil(rows * (cols - 1) / 5)
        n_hchars = _math.ceil((rows - 1) * cols / 5)
        vborders, hborders, _ = decode_regions(cols, rows, data)
        clue_data = data[n_vchars + n_hchars:]
        clues = decode_firefly(cols, rows, clue_data)
        return RegionArrowPuzzle(puzzle_type=puzzle_type, cols=cols, rows=rows,
                                title=title, date=date, url=url,
                                vborders=vborders, hborders=hborders, clues=clues)
    elif puzzle_type == "moonsun":
        import math as _math
        n_vchars = _math.ceil(rows * (cols - 1) / 5)
        n_hchars = _math.ceil((rows - 1) * cols / 5)
        vborders, hborders, _ = decode_regions(cols, rows, data)
        clue_data = data[n_vchars + n_hchars:]
        # Base-3 decode: each char encodes 3 cells (0=empty, 1=moon, 2=sun)
        cells = []
        for ch in clue_data:
            val = CHARS.index(ch)
            c2 = val % 3; val //= 3
            c1 = val % 3; val //= 3
            c0 = val
            cells.extend([c0, c1, c2])
        clues = []
        for i in range(min(len(cells), rows * cols)):
            if cells[i] != 0:
                clues.append((i // cols, i % cols, cells[i]))  # 1=moon, 2=sun
        return RegionPuzzle(puzzle_type=puzzle_type, cols=cols, rows=rows,
                           title=title, date=date, url=url,
                           vborders=vborders, hborders=hborders, clues=clues)
    elif puzzle_type == "tapa":
        clues = decode_tapa(cols, rows, data)
        return NurikabePuzzle(puzzle_type=puzzle_type, cols=cols, rows=rows,
                             title=title, date=date, url=url, clues=clues)
    elif puzzle_type == "sashigane":
        clues = decode_sashigane(cols, rows, data)
        return FireflyPuzzle(puzzle_type=puzzle_type, cols=cols, rows=rows,
                            title=title, date=date, url=url, clues=clues)
    elif puzzle_type == "dbchoco":
        import math as _math
        n_color = _math.ceil(cols * rows / 5)
        # Decode cell coloring
        bits = []
        for ch in data[:n_color]:
            val = CHARS.index(ch)
            for bit in range(4, -1, -1):
                bits.append((val >> bit) & 1)
        grey_cells = []
        for i in range(cols * rows):
            if bits[i]:
                grey_cells.append((i // cols, i % cols))
        # Decode clues
        clues = decode_nurikabe(cols, rows, data[n_color:])
        return DbchocoPuzzle(puzzle_type=puzzle_type, cols=cols, rows=rows,
                            title=title, date=date, url=url,
                            grey_cells=grey_cells, clues=clues)
    elif puzzle_type == "hebi":
        clues = decode_firefly(cols, rows, data)
        return FireflyPuzzle(puzzle_type=puzzle_type, cols=cols, rows=rows,
                            title=title, date=date, url=url, clues=clues)
    elif puzzle_type == "yajirin":
        clues = decode_firefly(cols, rows, data)
        return FireflyPuzzle(puzzle_type=puzzle_type, cols=cols, rows=rows,
                            title=title, date=date, url=url, clues=clues)
    elif puzzle_type == "firefly":
        clues = decode_firefly(cols, rows, data)
        return FireflyPuzzle(puzzle_type=puzzle_type, cols=cols, rows=rows,
                            title=title, date=date, url=url, clues=clues)
    elif puzzle_type == "icebarn":
        ice, arrows, in_arrow, out_arrow = decode_icebarn(cols, rows, data)
        return IceBarnPuzzle(puzzle_type=puzzle_type, cols=cols, rows=rows,
                            title=title, date=date, url=url,
                            ice=ice, arrows=arrows,
                            in_arrow=in_arrow, out_arrow=out_arrow)
    else:
        return UnknownPuzzle(puzzle_type=puzzle_type, cols=cols, rows=rows,
                            title=title, date=date, url=url)
