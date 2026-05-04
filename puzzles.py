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
class MashuPuzzle(Puzzle):
    """Masyu puzzle. Each clue is (row, col, value): 1=white circle, 2=black circle."""
    clues: list = field(default_factory=list)


@dataclass
class SimpleLoopPuzzle(Puzzle):
    """Simple Loop puzzle. blocked_cells are (row, col) where the loop cannot enter."""
    blocked_cells: list = field(default_factory=list)


@dataclass
class StarBattlePuzzle(Puzzle):
    """Star Battle puzzle. Regions + star count."""
    vborders: list = field(default_factory=list)
    hborders: list = field(default_factory=list)
    star_count: int = 1


@dataclass
class IcelomPuzzle(Puzzle):
    """Icelom puzzle. Ice cells + number clues + in/out arrows."""
    ice: list = field(default_factory=list)
    clues: list = field(default_factory=list)         # list of (row, col, value)
    in_arrow: int = 0
    out_arrow: int = 0


@dataclass
class BarnsPuzzle(Puzzle):
    """Barns puzzle. Ice cells + region borders."""
    ice: list = field(default_factory=list)
    vborders: list = field(default_factory=list)
    hborders: list = field(default_factory=list)


@dataclass
class ReflectPuzzle(Puzzle):
    """Reflect Link puzzle. Cells with mirrors and blocks.
    cells: list of (row, col, mirror_type, value)
    mirror_type: 0=block, 2=◣, 3=◢, 4=◤, 5=◥
    value: -1 for "no number".
    """
    cells: list = field(default_factory=list)


@dataclass
class SlalomPuzzle(Puzzle):
    """Slalom puzzle. Block cells + horizontal/vertical gate markers + a start position.
    cells: list of (row, col, kind, number) where:
      kind = 'block' (a numbered black cell)
      kind = 'gate_v' (vertical gate marker on the left edge of the cell)
      kind = 'gate_h' (horizontal gate marker on the top edge of the cell)
    number: integer label or None.
    start_row, start_col: position of the start marker (open circle).
    """
    cells: list = field(default_factory=list)
    start_row: int = -1
    start_col: int = -1


@dataclass
class KinkonkanPuzzle(Puzzle):
    """Kin-Kon-Kan puzzle. Region borders + edge clues with letter+number pairs.
    edge_clues: list of (side, idx, letter_idx, value) where
      side is 'top'/'bottom'/'left'/'right'
      idx is the column or row index along that side (0-indexed)
      letter_idx is the alphabetical letter index (1-based: 1='A', 2='B', ...)
      value is the number (-2 if just '.')
    """
    vborders: list = field(default_factory=list)
    hborders: list = field(default_factory=list)
    edge_clues: list = field(default_factory=list)


@dataclass
class WagiriPuzzle(Puzzle):
    """Wagiri puzzle. Intersection circle clues + cell number clues.
    cross_clues: (row, col, value) on (cols+1) x (rows+1) intersection grid.
    cell_clues: (row, col, value) for cell numbers; -2 means '.'.
    """
    cross_clues: list = field(default_factory=list)
    cell_clues: list = field(default_factory=list)


@dataclass
class ShwolfPuzzle(Puzzle):
    """Goats and Wolves puzzle. Cross dots + circles in cells.
    crosses: list of (row, col) — interior intersection (1..rows-1, 1..cols-1)
    circles: list of (row, col, value) where value 1 or 2 (sheep/wolf)
    """
    crosses: list = field(default_factory=list)
    circles: list = field(default_factory=list)


@dataclass
class UnknownPuzzle(Puzzle):
    """Placeholder for puzzle types we haven't implemented decoders for yet."""
    pass


def parse_url(url):
    """Extract puzzle_type, cols, rows, data from a puzz.link or pzv.jp URL.
    Some puzzles have a variant flag (single letter) before cols/rows; we skip it."""
    match = re.search(r'[?&]([^&]+)', url)
    if not match:
        return None, None, None, None
    query = match.group(1)
    parts = query.split("/")
    if len(parts) < 3:
        return None, None, None, None
    puzzle_type = parts[0]
    idx = 1
    # Skip variant flag if parts[1] isn't an int (e.g. slalom/d/10/10/, icelom/a/8/8/)
    if not parts[idx].isdigit():
        idx += 1
        if len(parts) < idx + 2:
            return None, None, None, None
    try:
        cols = int(parts[idx])
        rows = int(parts[idx + 1])
    except ValueError:
        return None, None, None, None
    data = "/".join(parts[idx + 2:]) if len(parts) > idx + 2 else ""
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

    # Decode clues from remaining data (best-effort; some callers ignore clues)
    clue_data = data[n_vchars + n_hchars:]
    clues = []
    if clue_data:
        try:
            clues = decode_nurikabe(cols, rows, clue_data)
        except ValueError:
            clues = []

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


def _read_number16(data, i):
    """Read one Number16 entry from data starting at i.
    Returns (value, consumed_chars). value=-1 if no value (skip char). value=-2 for '.'."""
    if i >= len(data):
        return -1, 0
    ca = data[i]
    if ca in "0123456789abcdef":
        return int(ca, 16), 1
    if ca == "-":
        return int(data[i + 1:i + 3], 16), 3
    if ca == "+":
        return int(data[i + 1:i + 4], 16), 4
    if ca == "=":
        return int(data[i + 1:i + 4], 16) + 4096, 4
    if ca == "%" or ca == "@":
        return int(data[i + 1:i + 4], 16) + 8192, 4
    if ca == "*":
        return int(data[i + 1:i + 5], 16) + 12240, 5
    if ca == "$":
        return int(data[i + 1:i + 6], 16) + 77776, 6
    if ca == ".":
        return -2, 1
    return -1, 0


def decode_number16(length, data):
    """Decode Number16-encoded data. Returns (list_of_(idx, value), consumed_chars).
    Each entry is a single integer value at a 0-indexed position in the cell array.
    """
    entries = []
    c = 0
    i = 0
    while i < len(data) and c < length:
        ca = data[i]
        val, consumed = _read_number16(data, i)
        if val != -1:
            entries.append((c, val))
            i += consumed
            c += 1
        elif "g" <= ca <= "z":
            c += int(ca, 36) - 15
            i += 1
        else:
            i += 1
    return entries, i


def decode_arrow_number16(length, data):
    """Decode arrow+number data (used by yajilin/yajikazu). Returns (entries, consumed).
    Each entry is (idx, qdir, qnum). qdir 0-4. qnum -2 for '.', -3 for '+' (no arrow black)."""
    entries = []
    c = 0
    i = 0
    while i < len(data) and c < length:
        ca = data[i]
        if ca == "+":
            entries.append((c, 0, -3))
            i += 1
            c += 1
        elif "0" <= ca <= "4":
            qdir = int(ca, 16)
            ca1 = data[i + 1] if i + 1 < len(data) else ""
            qnum = int(ca1, 16) if ca1 != "." else -2
            entries.append((c, qdir, qnum))
            i += 2
            c += 1
        elif "5" <= ca <= "9":
            qdir = int(ca, 16) - 5
            qnum = int(data[i + 1:i + 3], 16)
            entries.append((c, qdir, qnum))
            i += 3
            c += 1
        elif ca == "-":
            qdir = int(data[i + 1], 16)
            qnum = int(data[i + 2:i + 5], 16)
            entries.append((c, qdir, qnum))
            i += 5
            c += 1
        elif "a" <= ca <= "z":
            c += int(ca, 36) - 10
            i += 1
            c += 1
        else:
            i += 1
    return entries, i


def decode_binary(length, data):
    """Decode bit-packed binary data: 5 bits per char (base 32).
    Returns (list_of_indices_set, consumed_chars)."""
    indices = []
    c = 0
    twi = [16, 8, 4, 2, 1]
    i = 0
    while i < len(data) and c < length:
        num = int(data[i], 32)
        for w in range(5):
            if c < length:
                if num & twi[w]:
                    indices.append(c)
                c += 1
        i += 1
    return indices, i


def decode_triple(length, data):
    """Decode base-27 triple-encoded data (3 cells per char, value 0-2).
    Returns (list_of_(idx, val), consumed_chars). Only nonzero values returned."""
    entries = []
    c = 0
    tri = [9, 3, 1]
    pos = min((length + 2) // 3, len(data))
    for i in range(pos):
        ca = int(data[i], 27)
        for w in range(3):
            val = (ca // tri[w]) % 3
            if val > 0 and c < length:
                entries.append((c, val))
            c += 1
    return entries, pos


def decode_borders_only(cols, rows, data):
    """Decode just the vertical and horizontal borders. Returns (vborders, hborders, consumed)."""
    import math as _math
    n_vbits = rows * (cols - 1)
    n_hbits = (rows - 1) * cols
    n_vchars = _math.ceil(n_vbits / 5)
    n_hchars = _math.ceil(n_hbits / 5)
    vborders, hborders, _ = decode_regions(cols, rows, data)
    return vborders, hborders, n_vchars + n_hchars


def _find_room_top_cells(cols, rows, vborders, hborders):
    """Return a list of (row, col) for the top-left cell of each room, in row-major scan order."""
    rooms = _find_rooms(cols, rows, vborders, hborders)
    return [(r, c) for (r, c, _cells) in rooms]


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
    elif puzzle_type == "mashu":
        entries, _ = decode_triple(cols * rows, data)
        clues = [(idx // cols, idx % cols, val) for idx, val in entries]
        return MashuPuzzle(puzzle_type=puzzle_type, cols=cols, rows=rows,
                          title=title, date=date, url=url, clues=clues)
    elif puzzle_type in ("shikaku", "kurotto", "chainedb",
                          "hashi", "kurodoko", "mochikoro"):
        entries, _ = decode_number16(cols * rows, data)
        clues = [(idx // cols, idx % cols, val) for idx, val in entries]
        return NurikabePuzzle(puzzle_type=puzzle_type, cols=cols, rows=rows,
                             title=title, date=date, url=url, clues=clues)
    elif puzzle_type in ("sukoro", "view"):
        # Number10: digits 0-9 with '.' for empty marker.
        clues = []
        c = 0
        i = 0
        total = cols * rows
        while i < len(data) and c < total:
            ca = data[i]
            if ca == ".":
                clues.append((c // cols, c % cols, -2))
                c += 1
            elif "0" <= ca <= "9":
                clues.append((c // cols, c % cols, int(ca)))
                c += 1
            elif "a" <= ca <= "z":
                c += int(ca, 36) - 10 + 1
            else:
                c += 1
            i += 1
        return NurikabePuzzle(puzzle_type=puzzle_type, cols=cols, rows=rows,
                             title=title, date=date, url=url, clues=clues)
    elif puzzle_type == "fivecells":
        # decodeFivecells: '7' = block (ques=7); '.' = -2; '0'-'9' = number; 'a'-'z' = skip.
        clues = []
        c = 0
        i = 0
        total = cols * rows
        while i < len(data) and c < total:
            ca = data[i]
            if ca == "7":
                clues.append((c // cols, c % cols, -3))   # block marker
                c += 1
            elif ca == ".":
                clues.append((c // cols, c % cols, -2))
                c += 1
            elif "0" <= ca <= "9":
                clues.append((c // cols, c % cols, int(ca)))
                c += 1
            elif "a" <= ca <= "z":
                c += int(ca, 36) - 10 + 1
            else:
                c += 1
            i += 1
        return NurikabePuzzle(puzzle_type=puzzle_type, cols=cols, rows=rows,
                             title=title, date=date, url=url, clues=clues)
    elif puzzle_type == "factors":
        vborders, hborders, consumed = decode_borders_only(cols, rows, data)
        room_tops = _find_room_top_cells(cols, rows, vborders, hborders)
        entries, _ = decode_number16(len(room_tops), data[consumed:])
        clues = []
        for idx, val in entries:
            r, c_pos = room_tops[idx]
            clues.append((r, c_pos, val))
        return RegionPuzzle(puzzle_type=puzzle_type, cols=cols, rows=rows,
                           title=title, date=date, url=url,
                           vborders=vborders, hborders=hborders, clues=clues)
    elif puzzle_type == "wagiri":
        # decode4Cross on (cols+1)*(rows+1) intersections, then decodeNumber10 in cells.
        n_cross = (cols + 1) * (rows + 1)
        cross_clues = []
        c_pos = 0
        i = 0
        # Same encoding as decode_usoone_clues but operating on cross grid.
        cross_data_consumed = 0
        while i < len(data) and c_pos < n_cross:
            ca = data[i]
            if "0" <= ca <= "4":
                cross_clues.append((c_pos // (cols + 1), c_pos % (cols + 1), int(ca, 16)))
                c_pos += 1
            elif "5" <= ca <= "9":
                cross_clues.append((c_pos // (cols + 1), c_pos % (cols + 1), int(ca, 16) - 5))
                c_pos += 2
            elif "a" <= ca <= "e":
                cross_clues.append((c_pos // (cols + 1), c_pos % (cols + 1), int(ca, 16) - 10))
                c_pos += 3
            elif "g" <= ca <= "z":
                c_pos += int(ca, 36) - 16 + 1
            elif ca == ".":
                cross_clues.append((c_pos // (cols + 1), c_pos % (cols + 1), -2))
                c_pos += 1
            else:
                c_pos += 1
            i += 1
            cross_data_consumed = i
        rest = data[cross_data_consumed:]
        # decodeNumber10 for cell numbers.
        cell_clues = []
        c_pos = 0
        i = 0
        total = cols * rows
        while i < len(rest) and c_pos < total:
            ca = rest[i]
            if ca == ".":
                cell_clues.append((c_pos // cols, c_pos % cols, -2))
                c_pos += 1
            elif "0" <= ca <= "9":
                cell_clues.append((c_pos // cols, c_pos % cols, int(ca)))
                c_pos += 1
            elif "a" <= ca <= "z":
                c_pos += int(ca, 36) - 10 + 1
            else:
                c_pos += 1
            i += 1
        # Reuse WagiriPuzzle (new dataclass below)
        return WagiriPuzzle(puzzle_type=puzzle_type, cols=cols, rows=rows,
                           title=title, date=date, url=url,
                           cross_clues=cross_clues, cell_clues=cell_clues)
    elif puzzle_type in ("akari", "lightup"):
        clues = decode_usoone_clues(cols, rows, data, support_dot=True)
        return NurikabePuzzle(puzzle_type="akari", cols=cols, rows=rows,
                             title=title, date=date, url=url, clues=clues)
    elif puzzle_type == "shugaku":
        clues = []
        c = 0
        i = 0
        total = cols * rows
        while i < len(data) and c < total:
            ca = data[i]
            if "0" <= ca <= "4":
                clues.append((c // cols, c % cols, int(ca)))
                c += 1
            elif ca == "5":
                clues.append((c // cols, c % cols, -2))
                c += 1
            else:
                c += int(ca, 36) - 6 + 1
            i += 1
        return NurikabePuzzle(puzzle_type=puzzle_type, cols=cols, rows=rows,
                             title=title, date=date, url=url, clues=clues)
    elif puzzle_type == "simpleloop":
        blocked, _ = decode_binary(cols * rows, data)
        cells = [(idx // cols, idx % cols) for idx in blocked]
        return SimpleLoopPuzzle(puzzle_type=puzzle_type, cols=cols, rows=rows,
                               title=title, date=date, url=url, blocked_cells=cells)
    elif puzzle_type == "starbattle":
        parts = data.split("/")
        star_count = int(parts[0]) if parts and parts[0].isdigit() else 1
        border_data = "/".join(parts[1:])
        vborders, hborders, _ = decode_regions(cols, rows, border_data)
        return StarBattlePuzzle(puzzle_type=puzzle_type, cols=cols, rows=rows,
                               title=title, date=date, url=url,
                               vborders=vborders, hborders=hborders,
                               star_count=star_count)
    elif puzzle_type == "ayeheya":
        vborders, hborders, clues = decode_regions_roomclues(cols, rows, data)
        return RegionPuzzle(puzzle_type=puzzle_type, cols=cols, rows=rows,
                           title=title, date=date, url=url,
                           vborders=vborders, hborders=hborders, clues=clues)
    elif puzzle_type == "cocktail":
        vborders, hborders, consumed = decode_borders_only(cols, rows, data)
        room_tops = _find_room_top_cells(cols, rows, vborders, hborders)
        entries, _ = decode_number16(len(room_tops), data[consumed:])
        clues = []
        for idx, val in entries:
            r, c = room_tops[idx]
            clues.append((r, c, val))
        return RegionPuzzle(puzzle_type=puzzle_type, cols=cols, rows=rows,
                           title=title, date=date, url=url,
                           vborders=vborders, hborders=hborders, clues=clues)
    elif puzzle_type == "yajilin-regions":
        vborders, hborders, consumed = decode_borders_only(cols, rows, data)
        room_tops = _find_room_top_cells(cols, rows, vborders, hborders)
        entries, _ = decode_number16(len(room_tops), data[consumed:])
        clues = []
        for idx, val in entries:
            r, c = room_tops[idx]
            clues.append((r, c, val))
        return RegionPuzzle(puzzle_type=puzzle_type, cols=cols, rows=rows,
                           title=title, date=date, url=url,
                           vborders=vborders, hborders=hborders, clues=clues)
    elif puzzle_type == "yajikazu":
        entries, _ = decode_arrow_number16(cols * rows, data)
        clues = []
        for idx, qdir, qnum in entries:
            r, c = idx // cols, idx % cols
            if qnum == -3:
                # '+': black square no arrow
                clues.append((r, c, 0, None))
            else:
                val = None if qnum == -2 else qnum
                clues.append((r, c, qdir, val))
        return FireflyPuzzle(puzzle_type=puzzle_type, cols=cols, rows=rows,
                            title=title, date=date, url=url, clues=clues)
    elif puzzle_type in ("icelom", "icelom2"):
        # decodeIce (binary) then decodeNumber16 then '/in/out'
        ice_idx, consumed = decode_binary(cols * rows, data)
        ice = [(idx // cols, idx % cols) for idx in ice_idx]
        rest = data[consumed:]
        entries, n_consumed = decode_number16(cols * rows, rest)
        clues = [(idx // cols, idx % cols, val) for idx, val in entries]
        # Remaining: /in/out
        tail = rest[n_consumed:]
        in_arrow = out_arrow = 0
        if tail.startswith("/"):
            parts = tail[1:].split("/")
            if len(parts) >= 1 and parts[0].isdigit():
                in_arrow = int(parts[0])
            if len(parts) >= 2 and parts[1].isdigit():
                out_arrow = int(parts[1])
        return IcelomPuzzle(puzzle_type=puzzle_type, cols=cols, rows=rows,
                           title=title, date=date, url=url,
                           ice=ice, clues=clues,
                           in_arrow=in_arrow, out_arrow=out_arrow)
    elif puzzle_type == "barns":
        # decodeBarns (binary 5-bits) then decodeBorder
        ice_idx, consumed = decode_binary(cols * rows, data)
        ice = [(idx // cols, idx % cols) for idx in ice_idx]
        vborders, hborders, _ = decode_regions(cols, rows, data[consumed:])
        return BarnsPuzzle(puzzle_type=puzzle_type, cols=cols, rows=rows,
                          title=title, date=date, url=url,
                          ice=ice, vborders=vborders, hborders=hborders)
    elif puzzle_type == "reflect":
        cells = []
        c = 0
        i = 0
        total = cols * rows
        while i < len(data) and c < total:
            ca = data[i]
            if ca == "5":
                cells.append((c // cols, c % cols, 0, -1))  # block
                c += 1
                i += 1
            elif "1" <= ca <= "4":
                ques = int(ca) + 1  # 2-5
                qnum = int(data[i + 1], 16)
                if qnum == 0:
                    qnum = -1
                cells.append((c // cols, c % cols, ques, qnum))
                c += 1
                i += 2
            elif "6" <= ca <= "9":
                ques = int(ca) - 4  # 2-5
                qnum = int(data[i + 1:i + 3], 16)
                if qnum == 0:
                    qnum = -1
                cells.append((c // cols, c % cols, ques, qnum))
                c += 1
                i += 3
            elif "a" <= ca <= "z":
                c += int(ca, 36) - 10 + 1
                i += 1
            else:
                i += 1
        return ReflectPuzzle(puzzle_type=puzzle_type, cols=cols, rows=rows,
                            title=title, date=date, url=url, cells=cells)
    elif puzzle_type == "slalom":
        # parse_url already strips the variant flag.
        # Layout for the 'd' variant: <cell_types_and_numbers>/<start_index>
        parts = data.split("/")
        body = parts[0]
        start_index = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else -1
        block_positions = []      # row, col for each ques=1 cell, in scan order
        gate_cells = []           # (row, col, 'gate_h'|'gate_v')
        c = 0
        i = 0
        total = cols * rows
        while i < len(body) and c < total:
            ca = body[i]
            if ca == "1":
                block_positions.append((c // cols, c % cols))
                c += 1
                i += 1
            elif ca == "2":
                # ques=21 → vertical gate (vertical bar on left edge in pzprjs)
                gate_cells.append((c // cols, c % cols, "gate_v"))
                c += 1
                i += 1
            elif ca == "3":
                gate_cells.append((c // cols, c % cols, "gate_h"))
                c += 1
                i += 1
            elif "4" <= ca <= "9" or "a" <= ca <= "z":
                c += int(ca, 36) - 4 + 1
                i += 1
            else:
                i += 1
        # Phase 2: decode numbers for the block (ques=1) cells in cell scan order.
        # The encoder iterates all cells but only emits a value for ques=1 cells.
        block_numbers = {}
        bi = 0
        while i < len(body) and bi < len(block_positions):
            ca = body[i]
            if ca in "0123456789abcdef":
                block_numbers[bi] = int(ca, 16)
                bi += 1
                i += 1
            elif ca == "-":
                block_numbers[bi] = int(body[i + 1:i + 3], 16)
                bi += 1
                i += 3
            elif ca == ".":
                block_numbers[bi] = -2
                bi += 1
                i += 1
            else:
                i += 1
        cells = []
        for idx, (r, c_pos) in enumerate(block_positions):
            cells.append((r, c_pos, "block", block_numbers.get(idx)))
        for r, c_pos, kind in gate_cells:
            cells.append((r, c_pos, kind, None))
        sr, sc = -1, -1
        if 0 <= start_index < total:
            sr, sc = start_index // cols, start_index % cols
        return SlalomPuzzle(puzzle_type=puzzle_type, cols=cols, rows=rows,
                           title=title, date=date, url=url,
                           cells=cells, start_row=sr, start_col=sc)
    elif puzzle_type == "kinkonkan":
        # decodeBorder then decodeKinkonkan (excells with letter+number)
        vborders, hborders, consumed = decode_borders_only(cols, rows, data)
        rest = data[consumed:]
        # excells: 4 strips around the grid (top/bottom/left/right), each cols or rows long
        # The order in pzprjs is determined by board.excell — they are positioned at
        # negative coordinates in the bx/by grid system. We approximate by building
        # the 4 strips in the same scan order: top row (cols), bottom row (cols),
        # left col (rows), right col (rows).
        n_excell = 2 * (cols + rows)
        # Phase 1: positions with letter codes
        subint = []
        ec = 0
        i = 0
        excell_chars = {}
        while i < len(rest) and ec < n_excell:
            ca = rest[i]
            if "A" <= ca <= "Z":
                excell_chars[ec] = int(ca, 36) - 9
                subint.append(ec)
                ec += 1
                i += 1
            elif "0" <= ca <= "9":
                if i + 1 < len(rest):
                    excell_chars[ec] = int(rest[i + 1], 36) - 9 + (int(ca, 10) + 1) * 26
                    subint.append(ec)
                    ec += 1
                    i += 2
                else:
                    break
            elif "a" <= ca <= "z":
                ec += int(ca, 36) - 10 + 1
                i += 1
            else:
                i += 1
        # Phase 2: numbers for those positions
        excell_nums = {}
        ec = 0
        while i < len(rest) and ec < len(subint):
            ca = rest[i]
            if ca == ".":
                excell_nums[subint[ec]] = -2
                i += 1
            elif ca == "-":
                excell_nums[subint[ec]] = int(rest[i + 1:i + 3], 16)
                i += 3
            else:
                excell_nums[subint[ec]] = int(ca, 16)
                i += 1
            ec += 1
        # Convert excell ids to (side, idx). Order: top (cols), bottom (cols), left (rows), right (rows).
        edge_clues = []
        for ec_id, letter_idx in excell_chars.items():
            num = excell_nums.get(ec_id, -2)
            if ec_id < cols:
                side, idx = "top", ec_id
            elif ec_id < 2 * cols:
                side, idx = "bottom", ec_id - cols
            elif ec_id < 2 * cols + rows:
                side, idx = "left", ec_id - 2 * cols
            else:
                side, idx = "right", ec_id - 2 * cols - rows
            edge_clues.append((side, idx, letter_idx, num))
        return KinkonkanPuzzle(puzzle_type=puzzle_type, cols=cols, rows=rows,
                              title=title, date=date, url=url,
                              vborders=vborders, hborders=hborders,
                              edge_clues=edge_clues)
    elif puzzle_type == "shwolf":
        # decodeCrossMark then decodeCircle
        # CrossMark uses cross grid: (rows-1) x (cols-1) interior crosses
        cross_cols = cols - 1
        cross_rows = rows - 1
        n_cross = cross_cols * cross_rows
        crosses = []
        cc = 0
        i = 0
        while i < len(data) and cc < n_cross:
            ca = data[i]
            if "0" <= ca <= "9" or "a" <= ca <= "z":
                cc += int(ca, 36)
                if cc < n_cross:
                    cr = cc // cross_cols
                    cc_col = cc % cross_cols
                    crosses.append((cr, cc_col))
                cc += 1
            elif ca == ".":
                cc += 35
            i += 1
        rest = data[i:]
        # decodeCircle: triple base-27
        entries, _ = decode_triple(cols * rows, rest)
        circles = [(idx // cols, idx % cols, val) for idx, val in entries]
        return ShwolfPuzzle(puzzle_type=puzzle_type, cols=cols, rows=rows,
                           title=title, date=date, url=url,
                           crosses=crosses, circles=circles)
    else:
        return UnknownPuzzle(puzzle_type=puzzle_type, cols=cols, rows=rows,
                            title=title, date=date, url=url)
