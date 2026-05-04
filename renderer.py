"""PDF renderer for puzzles."""

import calendar
import math
import re

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from puzzles import (
    NurikabePuzzle, IceBarnPuzzle, RegionPuzzle, RegionArrowPuzzle, DbchocoPuzzle,
    MidloopPuzzle, PipelinkPuzzle, FireflyPuzzle, UnknownPuzzle,
    MashuPuzzle, SimpleLoopPuzzle, StarBattlePuzzle, IcelomPuzzle, BarnsPuzzle,
    ReflectPuzzle, SlalomPuzzle, KinkonkanPuzzle, ShwolfPuzzle, WagiriPuzzle,
)

# Register Japanese font
_JP_FONT = "DroidSansFallback"
pdfmetrics.registerFont(TTFont(_JP_FONT, "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf"))

PAGE_W, PAGE_H = A4
MARGIN = 20 * mm
HEADER_HEIGHT = 20 * mm

# English names for puzzle types
ENGLISH_NAMES = {
    "nurikabe": "Nurikabe",
    "fillomino": "Fillomino",
    "hitori": "Hitori",
    "icebarn": "Ice Barn",
    "nanro": "Nanro",
    "lits": "LITS",
    "shimaguni": "Islands",
    "country": "Country Road",
    "norinori": "Norinori",
    "heyawake": "Heyawake",
    "usoone": "Uso-one",
    "slither": "Slitherlink",
    "mashu": "Masyu",
    "tapa": "Tapa",
    "shakashaka": "Shakashaka",
    "gokigen": "Gokigen Naname",
    "yajirin": "Yajilin",
    "midloop": "Mid-loop",
    "simpleloop": "Simple Loop",
    "bag": "Bag",
    "starbattle": "Star Battle",
    "dbchoco": "Double Choco",
    "firefly": "Hotaru Beam",
    "numlin": "Numberlink",
    "pipelink": "Pipelink",
    "ringring": "Ring Ring",
    "moonsun": "Moon or Sun",
    "sashigane": "Sashigane",
    "chainedb": "Chained Block",
    "kurotto": "Kurotto",
    "hebi": "Hebi-Ichigo",
    "kuroclone": "Kuroclone",
    "koburin": "Koburin",
    "kinkonkan": "Kin-Kon-Kan",
    "kakuro": "Kakuro",
    "shikaku": "Shikaku",
    "bdblock": "Border Block",
    "lightup": "Akari",
    "akari": "Akari",
    "icelom": "Icelom",
    "icelom2": "Icelom 2",
    "slalom": "Slalom",
    "kurodoko": "Kurodoko",
    "mochikoro": "Mochikoro",
    "sukoro": "Sukoro",
    "wagiri": "Wagiri",
    "factors": "Rooms of Factors",
    "shugaku": "School Trip",
    "ayeheya": "Aye-Heya",
    "yajikazu": "Yajikazu",
    "reflect": "Reflect Link",
    "factors": "Rooms of Factors",
    "kurodoko": "Kurodoko",
    "fivecells": "Five Cells",
    "tasquare": "Tasquare",
    "cocktail": "Cocktail Lamp",
    "cbblock": "Color Block",
    "mochikoro": "Mochikoro",
    "paintarea": "Paint Area",
    "hashikake": "Hashiwokakero",
    "nuribou": "Nuribou",
    "wagiri": "Wagiri",
    "chocona": "Chocona",
    "creek": "Creek",
    "sukoro": "Sukoro",
    "barns": "Barns",
    "nurimaze": "Nurimaze",
    "tateyoko": "Tateyoko",
    "tatamibari": "Tatamibari",
    "yosenabe": "Yosenabe",
    "sudoku": "Sudoku",
    "hashi": "Hashiwokakero",
    "makaro": "Makaro",
    "view": "View",
    "snakes": "Snakes",
    "shwolf": "Sheep and Wolves",
    "yajilin-regions": "Regional Yajilin",
}

# Fullwidth digit mapping
_FW_DIGITS = "０１２３４５６７８９"


def _extract_number(title):
    """Extract the puzzle number from a Japanese title using fullwidth digits."""
    fw_digits = [c for c in title if c in _FW_DIGITS]
    if fw_digits:
        return int("".join(str(_FW_DIGITS.index(c)) for c in fw_digits))
    return None


def _extract_date(date_str):
    """Extract YYYY-MM-DD from Japanese date like '2026年02月15日'."""
    m = re.search(r'(\d{4}).*?(\d{1,2}).*?(\d{1,2})', date_str)
    if m:
        return f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
    return date_str


def _english_header(puzzle):
    """Return English header like 'Nurikabe 367  2026-02-15'."""
    name = ENGLISH_NAMES.get(puzzle.puzzle_type, puzzle.puzzle_type)
    num = _extract_number(puzzle.title)
    date = _extract_date(puzzle.date)
    if num is not None:
        return f"{name} {num}  {date}"
    return f"{name}  {date}"


def _draw_header(c, puzzle, page_w, page_h):
    """Draw title and date at the top of the page."""
    # English header
    header = _english_header(puzzle)
    if puzzle.stars:
        header += "  " + "*" * puzzle.stars
    c.setFont("Helvetica-Bold", 14)
    c.drawString(MARGIN, page_h - MARGIN, header)
    # Japanese title below
    c.setFont(_JP_FONT, 10)
    c.drawString(MARGIN, page_h - MARGIN - 16, puzzle.title)


def _calc_grid_params(puzzle, page_w, page_h):
    """Calculate cell size and grid origin for centering the grid on the page."""
    available_w = page_w - 2 * MARGIN
    available_h = page_h - 2 * MARGIN - HEADER_HEIGHT
    cell_size = min(available_w / puzzle.cols, available_h / puzzle.rows)
    grid_w = cell_size * puzzle.cols
    grid_h = cell_size * puzzle.rows
    x0 = MARGIN + (available_w - grid_w) / 2
    y_top = page_h - MARGIN - HEADER_HEIGHT
    y0 = y_top - (available_h - grid_h) / 2 - grid_h  # bottom-left of grid
    return cell_size, x0, y0


def _draw_grid(c, rows, cols, cell_size, x0, y0):
    """Draw a basic grid of lines."""
    c.setStrokeColorRGB(0, 0, 0)
    c.setLineWidth(0.5)
    for i in range(rows + 1):
        y = y0 + i * cell_size
        c.line(x0, y, x0 + cols * cell_size, y)
    for j in range(cols + 1):
        x = x0 + j * cell_size
        c.line(x, y0, x, y0 + rows * cell_size)
    # Thicker border
    c.setLineWidth(2)
    c.rect(x0, y0, cols * cell_size, rows * cell_size, stroke=1, fill=0)


def _cell_center(row, col, rows, cell_size, x0, y0):
    """Return the center (cx, cy) of a cell. Row 0 is the top row."""
    cx = x0 + (col + 0.5) * cell_size
    cy = y0 + (rows - row - 0.5) * cell_size
    return cx, cy


def render_nurikabe(c, puzzle):
    cell_size, x0, y0 = _calc_grid_params(puzzle, PAGE_W, PAGE_H)
    if puzzle.puzzle_type == "ringring":
        # Dashed grid for ring ring
        c.setStrokeColorRGB(0.5, 0.5, 0.5)
        c.setLineWidth(0.5)
        c.setDash(3, 3)
        for i in range(puzzle.rows + 1):
            y = y0 + i * cell_size
            c.line(x0, y, x0 + puzzle.cols * cell_size, y)
        for j in range(puzzle.cols + 1):
            x = x0 + j * cell_size
            c.line(x, y0, x, y0 + puzzle.rows * cell_size)
        c.setDash()
        c.setStrokeColorRGB(0, 0, 0)
        c.setLineWidth(2)
        c.rect(x0, y0, puzzle.cols * cell_size, puzzle.rows * cell_size, stroke=1, fill=0)
    elif puzzle.puzzle_type != "slither":
        _draw_grid(c, puzzle.rows, puzzle.cols, cell_size, x0, y0)

    is_shakashaka = puzzle.puzzle_type in ("shakashaka", "ringring", "akari")
    is_tapa = puzzle.puzzle_type == "tapa"
    is_slither = puzzle.puzzle_type == "slither"
    is_kurotto = puzzle.puzzle_type == "kurotto"
    is_chainedb = puzzle.puzzle_type == "chainedb"
    is_shugaku = puzzle.puzzle_type == "shugaku"
    is_hashi = puzzle.puzzle_type == "hashi"
    is_fivecells = puzzle.puzzle_type == "fivecells"

    is_gokigen = puzzle.puzzle_type == "gokigen"

    if is_slither:
        # Slitherlink: dots at corners, no grid lines
        dot_r = cell_size * 0.06
        c.setFillColorRGB(0, 0, 0)
        for i in range(puzzle.rows + 1):
            for j in range(puzzle.cols + 1):
                x = x0 + j * cell_size
                y = y0 + (puzzle.rows - i) * cell_size
                c.circle(x, y, dot_r, stroke=0, fill=1)

    if is_gokigen:
        # Gokigen: dashed grid lines + circles with numbers at intersections
        cell_size = min((PAGE_W - 2 * MARGIN) / puzzle.cols,
                       (PAGE_H - 2 * MARGIN - HEADER_HEIGHT) / puzzle.rows)
        grid_w = cell_size * puzzle.cols
        grid_h = cell_size * puzzle.rows
        x0 = MARGIN + ((PAGE_W - 2 * MARGIN) - grid_w) / 2
        y_top = PAGE_H - MARGIN - HEADER_HEIGHT
        y0 = y_top - ((PAGE_H - 2 * MARGIN - HEADER_HEIGHT) - grid_h) / 2 - grid_h
        # Dashed grid
        c.setStrokeColorRGB(0.5, 0.5, 0.5)
        c.setLineWidth(0.5)
        c.setDash(3, 3)
        for i in range(puzzle.rows + 1):
            y = y0 + i * cell_size
            c.line(x0, y, x0 + puzzle.cols * cell_size, y)
        for j in range(puzzle.cols + 1):
            x = x0 + j * cell_size
            c.line(x, y0, x, y0 + puzzle.rows * cell_size)
        c.setDash()
        radius = cell_size * 0.2
        font_size = min(radius * 1.4, 14)
        for row, col, val in puzzle.clues:
            # Intersection position
            ix = x0 + col * cell_size
            iy = y0 + (puzzle.rows - row) * cell_size
            # White circle with border
            c.setFillColorRGB(1, 1, 1)
            c.setStrokeColorRGB(0, 0, 0)
            c.setLineWidth(1.5)
            c.circle(ix, iy, radius, stroke=1, fill=1)
            # Number
            c.setFillColorRGB(0, 0, 0)
            c.setFont("Helvetica-Bold", font_size)
            c.drawCentredString(ix, iy - font_size * 0.3, str(val))
        return

    font_size = min(cell_size * 0.6, 20)

    for row, col, val in puzzle.clues:
        cx, cy = _cell_center(row, col, puzzle.rows, cell_size, x0, y0)
        if is_kurotto:
            # White circle, with optional number; -2 = empty circle
            c.setStrokeColorRGB(0, 0, 0)
            c.setFillColorRGB(1, 1, 1)
            c.setLineWidth(1.5)
            c.circle(cx, cy, cell_size * 0.35, stroke=1, fill=1)
            if val >= 0:
                c.setFillColorRGB(0, 0, 0)
                c.setFont("Helvetica-Bold", font_size)
                c.drawCentredString(cx, cy - font_size * 0.3, str(val))
        elif is_chainedb:
            # Grey background cell with optional number; -2 = empty grey cell
            c.setFillColorRGB(0.7, 0.7, 0.7)
            c.rect(cx - cell_size / 2, cy - cell_size / 2,
                   cell_size, cell_size, stroke=0, fill=1)
            if val >= 0:
                c.setFillColorRGB(0, 0, 0)
                c.setFont("Helvetica-Bold", font_size)
                c.drawCentredString(cx, cy - font_size * 0.3, str(val))
        elif is_shakashaka:
            # Draw black cell
            c.setFillColorRGB(0, 0, 0)
            c.rect(cx - cell_size / 2, cy - cell_size / 2,
                   cell_size, cell_size, stroke=0, fill=1)
            if val >= 0:
                # White number on black cell
                c.setFillColorRGB(1, 1, 1)
                c.setFont("Helvetica-Bold", font_size)
                c.drawCentredString(cx, cy - font_size * 0.3, str(val))
            c.setFillColorRGB(0, 0, 0)
        elif is_tapa:
            # Tapa: multi-value clues positioned within cell
            lines = str(val).split('\n')
            n = len(lines)
            off = cell_size * 0.25  # offset from center
            if n == 1:
                # Single: centered
                fs = min(cell_size * 0.6, 20)
                c.setFont("Helvetica-Bold", fs)
                c.drawCentredString(cx, cy - fs * 0.3, lines[0])
            elif n == 2:
                # Double: top-left / bottom-right
                fs = min(cell_size * 0.4, 16)
                c.setFont("Helvetica-Bold", fs)
                c.drawCentredString(cx - off, cy + off - fs * 0.3, lines[0])
                c.drawCentredString(cx + off, cy - off - fs * 0.3, lines[1])
            elif n == 3:
                # Triple: top-left / top-right / bottom-middle
                fs = min(cell_size * 0.35, 14)
                c.setFont("Helvetica-Bold", fs)
                c.drawCentredString(cx - off, cy + off - fs * 0.3, lines[0])
                c.drawCentredString(cx + off, cy + off - fs * 0.3, lines[1])
                c.drawCentredString(cx, cy - off - fs * 0.3, lines[2])
            elif n == 4:
                # Quad: top-left / top-right / bottom-left / bottom-right
                fs = min(cell_size * 0.3, 12)
                c.setFont("Helvetica-Bold", fs)
                c.drawCentredString(cx - off, cy + off - fs * 0.3, lines[0])
                c.drawCentredString(cx + off, cy + off - fs * 0.3, lines[1])
                c.drawCentredString(cx - off, cy - off - fs * 0.3, lines[2])
                c.drawCentredString(cx + off, cy - off - fs * 0.3, lines[3])
        elif is_shugaku:
            # Render -2 as "?" (pillow without count) and others as the number.
            text = "?" if val == -2 else str(val)
            c.setFont("Helvetica-Bold", font_size)
            c.drawCentredString(cx, cy - font_size * 0.3, text)
        elif is_hashi:
            # Hashi: number in a circle (island)
            c.setStrokeColorRGB(0, 0, 0)
            c.setFillColorRGB(1, 1, 1)
            c.setLineWidth(1.5)
            c.circle(cx, cy, cell_size * 0.4, stroke=1, fill=1)
            if val >= 0:
                c.setFillColorRGB(0, 0, 0)
                c.setFont("Helvetica-Bold", font_size)
                c.drawCentredString(cx, cy - font_size * 0.3, str(val))
        elif is_fivecells:
            if val == -3:
                # Block cell (ques=7)
                c.setFillColorRGB(0, 0, 0)
                c.rect(cx - cell_size / 2, cy - cell_size / 2,
                       cell_size, cell_size, stroke=0, fill=1)
            elif val == -2:
                c.setFillColorRGB(0, 0, 0)
                c.setFont("Helvetica-Bold", font_size)
                c.drawCentredString(cx, cy - font_size * 0.3, "?")
            else:
                c.setFillColorRGB(0, 0, 0)
                c.setFont("Helvetica-Bold", font_size)
                c.drawCentredString(cx, cy - font_size * 0.3, str(val))
        else:
            c.setFont("Helvetica-Bold", font_size)
            c.drawCentredString(cx, cy - font_size * 0.3, str(val))


def render_icebarn(c, puzzle):
    cell_size, x0, y0 = _calc_grid_params(puzzle, PAGE_W, PAGE_H)
    _draw_grid(c, puzzle.rows, puzzle.cols, cell_size, x0, y0)

    # Draw ice cells (shaded)
    c.setFillColorRGB(0.8, 0.9, 1.0)
    for row, col in puzzle.ice:
        cx, cy = _cell_center(row, col, puzzle.rows, cell_size, x0, y0)
        c.rect(cx - cell_size / 2, cy - cell_size / 2, cell_size, cell_size, stroke=0, fill=1)
    c.setFillColorRGB(0, 0, 0)

    # Redraw grid on top of shading
    _draw_grid(c, puzzle.rows, puzzle.cols, cell_size, x0, y0)

    # Draw arrows
    arrow_size = cell_size * 0.3
    for row, col, dr, dc, atype in puzzle.arrows:
        if atype in ("in", "out"):
            cx = x0 + (col + 0.5) * cell_size
            cy = y0 + (puzzle.rows - row - 0.5) * cell_size
            if atype == "in":
                cx = x0 + (col + 0.5) * cell_size + dc * cell_size * 0.5
                cy = y0 + (puzzle.rows - row - 0.5) * cell_size - dr * cell_size * 0.5
        else:
            cx = x0 + (col + 0.5) * cell_size + dc * cell_size * 0.5
            cy = y0 + (puzzle.rows - row - 0.5) * cell_size - dr * cell_size * 0.5

        _draw_arrow(c, cx, cy, dr, dc, arrow_size)


def _draw_arrow(c, cx, cy, dr, dc, size):
    """Draw a small arrow at (cx, cy) pointing in direction (dr, dc)."""
    dx, dy = dc * size, -dr * size
    c.setLineWidth(1.5)
    c.line(cx - dx * 0.5, cy - dy * 0.5, cx + dx * 0.5, cy + dy * 0.5)
    head_size = size * 0.5
    angle = math.atan2(dy, dx)
    for offset in [2.7, -2.7]:
        ha = angle + offset
        c.line(cx + dx * 0.5, cy + dy * 0.5,
               cx + dx * 0.5 + head_size * math.cos(ha),
               cy + dy * 0.5 + head_size * math.sin(ha))


def render_region(c, puzzle):
    cell_size, x0, y0 = _calc_grid_params(puzzle, PAGE_W, PAGE_H)

    # Draw thin grid lines
    c.setStrokeColorRGB(0.7, 0.7, 0.7)
    c.setLineWidth(0.5)
    for i in range(puzzle.rows + 1):
        y = y0 + i * cell_size
        c.line(x0, y, x0 + puzzle.cols * cell_size, y)
    for j in range(puzzle.cols + 1):
        x = x0 + j * cell_size
        c.line(x, y0, x, y0 + puzzle.rows * cell_size)

    # Draw thick region borders
    c.setStrokeColorRGB(0, 0, 0)
    c.setLineWidth(2.5)

    # Outer border
    c.rect(x0, y0, puzzle.cols * cell_size, puzzle.rows * cell_size, stroke=1, fill=0)

    # Vertical borders: (row, col) means border between col and col+1 in that row
    for row, col in puzzle.vborders:
        x = x0 + (col + 1) * cell_size
        y_top = y0 + (puzzle.rows - row) * cell_size
        y_bot = y_top - cell_size
        c.line(x, y_bot, x, y_top)

    # Horizontal borders: (row, col) means border between row and row+1 in that col
    for row, col in puzzle.hborders:
        y = y0 + (puzzle.rows - row - 1) * cell_size
        x_left = x0 + col * cell_size
        x_right = x_left + cell_size
        c.line(x_left, y, x_right, y)

    # Draw clues
    if puzzle.clues:
        is_moonsun = puzzle.puzzle_type == "moonsun"
        if is_moonsun:
            radius = cell_size * 0.3
            for row, col, val in puzzle.clues:
                cx, cy = _cell_center(row, col, puzzle.rows, cell_size, x0, y0)
                if val == 1:  # Sun = open circle
                    c.setStrokeColorRGB(0, 0, 0)
                    c.setFillColorRGB(1, 1, 1)
                    c.setLineWidth(1.5)
                    c.circle(cx, cy, radius, stroke=1, fill=1)
                else:  # Moon = filled crescent
                    c.setFillColorRGB(0, 0, 0)
                    c.circle(cx, cy, radius, stroke=0, fill=1)
                    c.setFillColorRGB(1, 1, 1)
                    c.circle(cx + radius * 0.4, cy, radius * 0.85, stroke=0, fill=1)
        else:
            font_size = min(cell_size * 0.6, 20)
            c.setFont("Helvetica-Bold", font_size)
            for row, col, val in puzzle.clues:
                cx, cy = _cell_center(row, col, puzzle.rows, cell_size, x0, y0)
                c.drawCentredString(cx, cy - font_size * 0.3, str(val))


def render_region_arrow(c, puzzle):
    """Render region puzzle with arrow clues (kuroclone)."""
    # Draw regions (reuse region renderer logic)
    cell_size, x0, y0 = _calc_grid_params(puzzle, PAGE_W, PAGE_H)

    # Thin grid
    c.setStrokeColorRGB(0.7, 0.7, 0.7)
    c.setLineWidth(0.5)
    for i in range(puzzle.rows + 1):
        y = y0 + i * cell_size
        c.line(x0, y, x0 + puzzle.cols * cell_size, y)
    for j in range(puzzle.cols + 1):
        x = x0 + j * cell_size
        c.line(x, y0, x, y0 + puzzle.rows * cell_size)

    # Thick region borders
    c.setStrokeColorRGB(0, 0, 0)
    c.setLineWidth(2.5)
    c.rect(x0, y0, puzzle.cols * cell_size, puzzle.rows * cell_size, stroke=1, fill=0)
    for row, col in puzzle.vborders:
        x = x0 + (col + 1) * cell_size
        y_top = y0 + (puzzle.rows - row) * cell_size
        c.line(x, y_top - cell_size, x, y_top)
    for row, col in puzzle.hborders:
        y = y0 + (puzzle.rows - row - 1) * cell_size
        c.line(x0 + col * cell_size, y, x0 + (col + 1) * cell_size, y)

    # Draw arrow clues (same as yajilin)
    dir_vectors = {1: (0, 1), 2: (0, -1), 3: (-1, 0), 4: (1, 0)}
    font_size = min(cell_size * 0.4, 16)
    for row, col, direction, val in puzzle.clues:
        cx, cy = _cell_center(row, col, puzzle.rows, cell_size, x0, y0)
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica-Bold", font_size)
        c.drawCentredString(cx, cy - font_size * 0.3, str(val))
        # Triangle arrow
        dx, dy = dir_vectors[direction]
        tri_size = cell_size * 0.12
        tip_x = cx + dx * cell_size * 0.4
        tip_y = cy + dy * cell_size * 0.4
        base1_x = tip_x - dx * tri_size * 2 + dy * tri_size
        base1_y = tip_y - dy * tri_size * 2 - dx * tri_size
        base2_x = tip_x - dx * tri_size * 2 - dy * tri_size
        base2_y = tip_y - dy * tri_size * 2 + dx * tri_size
        p = c.beginPath()
        p.moveTo(tip_x, tip_y)
        p.lineTo(base1_x, base1_y)
        p.lineTo(base2_x, base2_y)
        p.close()
        c.drawPath(p, fill=1, stroke=0)


def render_dbchoco(c, puzzle):
    """Render Double Choco. Grey/white cells with dashed grid and numbers."""
    cell_size, x0, y0 = _calc_grid_params(puzzle, PAGE_W, PAGE_H)

    # Draw grey cells
    c.setFillColorRGB(0.8, 0.8, 0.8)
    for row, col in puzzle.grey_cells:
        cx, cy = _cell_center(row, col, puzzle.rows, cell_size, x0, y0)
        c.rect(cx - cell_size / 2, cy - cell_size / 2, cell_size, cell_size, stroke=0, fill=1)
    c.setFillColorRGB(0, 0, 0)

    # Dashed grid
    c.setStrokeColorRGB(0.5, 0.5, 0.5)
    c.setLineWidth(0.5)
    c.setDash(3, 3)
    for i in range(puzzle.rows + 1):
        y = y0 + i * cell_size
        c.line(x0, y, x0 + puzzle.cols * cell_size, y)
    for j in range(puzzle.cols + 1):
        x = x0 + j * cell_size
        c.line(x, y0, x, y0 + puzzle.rows * cell_size)
    c.setDash()

    # Solid outer border
    c.setStrokeColorRGB(0, 0, 0)
    c.setLineWidth(2)
    c.rect(x0, y0, puzzle.cols * cell_size, puzzle.rows * cell_size, stroke=1, fill=0)

    # Draw clues
    font_size = min(cell_size * 0.6, 20)
    c.setFont("Helvetica-Bold", font_size)
    c.setFillColorRGB(0, 0, 0)
    for row, col, val in puzzle.clues:
        cx, cy = _cell_center(row, col, puzzle.rows, cell_size, x0, y0)
        c.drawCentredString(cx, cy - font_size * 0.3, str(val))


def render_midloop(c, puzzle):
    """Render midloop. Grid with dots at cell centers and edges."""
    available_w = PAGE_W - 2 * MARGIN
    available_h = PAGE_H - 2 * MARGIN - HEADER_HEIGHT
    cell_size = min(available_w / puzzle.cols, available_h / puzzle.rows)
    grid_w = cell_size * puzzle.cols
    grid_h = cell_size * puzzle.rows
    x0 = MARGIN + (available_w - grid_w) / 2
    y_top = PAGE_H - MARGIN - HEADER_HEIGHT
    y0 = y_top - (available_h - grid_h) / 2 - grid_h

    _draw_grid(c, puzzle.rows, puzzle.cols, cell_size, x0, y0)

    # Draw dots
    dot_radius = cell_size * 0.1
    c.setFillColorRGB(0, 0, 0)
    half = cell_size * 0.5

    for fr, fc in puzzle.dots:
        # Convert fine grid coords to page coords
        # fine_row 0 = top of grid (row 0 center), fine_row 1 = between row 0 and 1, etc.
        px = x0 + (fc + 1) * half
        py = y0 + (2 * puzzle.rows - 1 - fr) * half
        c.circle(px, py, dot_radius, stroke=0, fill=1)


def render_pipelink(c, puzzle):
    cell_size, x0, y0 = _calc_grid_params(puzzle, PAGE_W, PAGE_H)
    # Dashed grid
    c.setStrokeColorRGB(0.5, 0.5, 0.5)
    c.setLineWidth(0.5)
    c.setDash(3, 3)
    for i in range(puzzle.rows + 1):
        y = y0 + i * cell_size
        c.line(x0, y, x0 + puzzle.cols * cell_size, y)
    for j in range(puzzle.cols + 1):
        x = x0 + j * cell_size
        c.line(x, y0, x, y0 + puzzle.rows * cell_size)
    c.setDash()
    # Outer border solid
    c.setStrokeColorRGB(0, 0, 0)
    c.setLineWidth(2)
    c.rect(x0, y0, puzzle.cols * cell_size, puzzle.rows * cell_size, stroke=1, fill=0)

    # Pipe connections as (dx, dy) in PDF coords from cell center to edge
    # dx>0 = right, dy>0 = up
    # 0=cross ┼, 1=vertical │, 2=horizontal ─,
    # 3=bend ┘ (left+up), 4=bend └ (right+up), 5=bend ┐ (left+down), 6=bend ┌ (right+down)
    pipe_edges = {
        0: [(0, 1), (0, -1), (-1, 0), (1, 0)],  # cross: all 4
        1: [(0, 1), (0, -1)],                     # vertical: up, down
        2: [(-1, 0), (1, 0)],                     # horizontal: left, right
        3: [(1, 0), (0, 1)],                      # ┘: right, up
        4: [(-1, 0), (0, 1)],                     # └: left, up
        5: [(-1, 0), (0, -1)],                    # ┐: left, down
        6: [(1, 0), (0, -1)],                     # ┌: right, down
    }

    c.setStrokeColorRGB(0, 0, 0)
    c.setLineWidth(3)
    c.setLineCap(1)  # round caps
    half = cell_size * 0.5

    for row, col, pipe_type in puzzle.segments:
        cx, cy = _cell_center(row, col, puzzle.rows, cell_size, x0, y0)
        edges = pipe_edges[pipe_type]
        for dx, dy in edges:
            c.line(cx, cy, cx + dx * half, cy + dy * half)


def render_firefly(c, puzzle):
    """Render Hotaru Beam or Yajilin. Both have direction+number clues."""
    is_yajilin = puzzle.puzzle_type in ("yajirin", "hebi", "yajikazu")
    is_sashigane = puzzle.puzzle_type == "sashigane"

    if is_sashigane:
        # Sashigane: dashed grid, arrows and circles in cells
        cell_size, x0, y0 = _calc_grid_params(puzzle, PAGE_W, PAGE_H)
        c.setStrokeColorRGB(0.5, 0.5, 0.5)
        c.setLineWidth(0.5)
        c.setDash(3, 3)
        for i in range(puzzle.rows + 1):
            y = y0 + i * cell_size
            c.line(x0, y, x0 + puzzle.cols * cell_size, y)
        for j in range(puzzle.cols + 1):
            x = x0 + j * cell_size
            c.line(x, y0, x, y0 + puzzle.rows * cell_size)
        c.setDash()
        c.setStrokeColorRGB(0, 0, 0)
        c.setLineWidth(2)
        c.rect(x0, y0, puzzle.cols * cell_size, puzzle.rows * cell_size, stroke=1, fill=0)
    elif is_yajilin:
        # Yajilin: clues in cells on a regular grid
        cell_size, x0, y0 = _calc_grid_params(puzzle, PAGE_W, PAGE_H)
        _draw_grid(c, puzzle.rows, puzzle.cols, cell_size, x0, y0)
    else:
        # Firefly: clues on intersections of a dashed grid
        available_w = PAGE_W - 2 * MARGIN
        available_h = PAGE_H - 2 * MARGIN - HEADER_HEIGHT
        cell_size = min(available_w / (puzzle.cols - 1), available_h / (puzzle.rows - 1))
        grid_w = cell_size * (puzzle.cols - 1)
        grid_h = cell_size * (puzzle.rows - 1)
        x0 = MARGIN + (available_w - grid_w) / 2
        y_top = PAGE_H - MARGIN - HEADER_HEIGHT
        y0 = y_top - (available_h - grid_h) / 2 - grid_h

        # Draw dashed grid
        c.setStrokeColorRGB(0.5, 0.5, 0.5)
        c.setLineWidth(0.5)
        c.setDash(3, 3)
        for i in range(puzzle.rows):
            y = y0 + i * cell_size
            c.line(x0, y, x0 + (puzzle.cols - 1) * cell_size, y)
        for j in range(puzzle.cols):
            x = x0 + j * cell_size
            c.line(x, y0, x, y0 + (puzzle.rows - 1) * cell_size)
        c.setDash()

    # Direction vectors: 1=up, 2=down, 3=left, 4=right
    dir_vectors = {1: (0, 1), 2: (0, -1), 3: (-1, 0), 4: (1, 0)}
    # Arrow symbols for yajilin
    arrow_chars = {1: "\u2191", 2: "\u2193", 3: "\u2190", 4: "\u2192"}

    radius = cell_size * 0.25
    tail_len = cell_size * 0.25

    for row, col, direction, val in puzzle.clues:
        if is_sashigane:
            cx, cy = _cell_center(row, col, puzzle.rows, cell_size, x0, y0)
            if direction == 0:
                # Circle (with or without number)
                radius = cell_size * 0.3
                c.setStrokeColorRGB(0, 0, 0)
                c.setFillColorRGB(1, 1, 1)
                c.setLineWidth(1.5)
                c.circle(cx, cy, radius, stroke=1, fill=1)
                if val is not None:
                    font_size = min(radius * 1.4, 14)
                    c.setFillColorRGB(0, 0, 0)
                    c.setFont("Helvetica-Bold", font_size)
                    c.drawCentredString(cx, cy - font_size * 0.3, str(val))
            else:
                # Arrow
                dx, dy = dir_vectors[direction]
                arrow_len = cell_size * 0.35
                c.setStrokeColorRGB(0, 0, 0)
                c.setLineWidth(2)
                c.line(cx - dx * arrow_len, cy - dy * arrow_len,
                       cx + dx * arrow_len, cy + dy * arrow_len)
                # Arrowhead
                tri_size = cell_size * 0.12
                tip_x = cx + dx * arrow_len
                tip_y = cy + dy * arrow_len
                base1_x = tip_x - dx * tri_size * 2 + dy * tri_size
                base1_y = tip_y - dy * tri_size * 2 - dx * tri_size
                base2_x = tip_x - dx * tri_size * 2 - dy * tri_size
                base2_y = tip_y - dy * tri_size * 2 + dx * tri_size
                c.setFillColorRGB(0, 0, 0)
                p = c.beginPath()
                p.moveTo(tip_x, tip_y)
                p.lineTo(base1_x, base1_y)
                p.lineTo(base2_x, base2_y)
                p.close()
                c.drawPath(p, fill=1, stroke=0)
            continue
        elif is_yajilin:
            # Cell center position
            cx, cy = _cell_center(row, col, puzzle.rows, cell_size, x0, y0)
            if direction == 0:
                # Black square
                c.setFillColorRGB(0, 0, 0)
                c.rect(cx - cell_size / 2, cy - cell_size / 2,
                       cell_size, cell_size, stroke=0, fill=1)
                continue
            is_hebi = puzzle.puzzle_type == "hebi"
            if is_hebi:
                # Black cell background
                c.setFillColorRGB(0, 0, 0)
                c.rect(cx - cell_size / 2, cy - cell_size / 2,
                       cell_size, cell_size, stroke=0, fill=1)
            # Draw number and arrow in cell
            font_size = min(cell_size * 0.4, 16)
            c.setFillColorRGB(1, 1, 1) if is_hebi else c.setFillColorRGB(0, 0, 0)
            c.setFont("Helvetica-Bold", font_size)
            c.drawCentredString(cx, cy - font_size * 0.3, str(val))
            # Draw arrow indicator
            arrow_size = cell_size * 0.15
            dx, dy = dir_vectors[direction]
            offset = cell_size * 0.3
            ax = cx + dx * offset
            ay = cy + dy * offset
            _draw_arrow(c, ax, ay, -dy, dx if dy == 0 else 0, arrow_size)
            # Actually just use a simple triangle
            c.setFillColorRGB(1, 1, 1) if is_hebi else c.setFillColorRGB(0, 0, 0)
            tri_size = cell_size * 0.12
            tip_x = cx + dx * cell_size * 0.4
            tip_y = cy + dy * cell_size * 0.4
            base1_x = tip_x - dx * tri_size * 2 + dy * tri_size
            base1_y = tip_y - dy * tri_size * 2 - dx * tri_size
            base2_x = tip_x - dx * tri_size * 2 - dy * tri_size
            base2_y = tip_y - dy * tri_size * 2 + dx * tri_size
            p = c.beginPath()
            p.moveTo(tip_x, tip_y)
            p.lineTo(base1_x, base1_y)
            p.lineTo(base2_x, base2_y)
            p.close()
            c.drawPath(p, fill=1, stroke=0)
        else:
            # Intersection position (row 0 = top)
            cx = x0 + col * cell_size
            cy = y0 + (puzzle.rows - 1 - row) * cell_size

            # Draw circle
            c.setStrokeColorRGB(0, 0, 0)
            c.setFillColorRGB(1, 1, 1)
            c.setLineWidth(1.5)
            c.circle(cx, cy, radius, stroke=1, fill=1)

            # Draw number inside circle
            font_size = min(radius * 1.4, 14)
            if val is not None:
                c.setFillColorRGB(0, 0, 0)
                c.setFont("Helvetica-Bold", font_size)
                c.drawCentredString(cx, cy - font_size * 0.3, str(val))

            # Draw tail
            dx, dy = dir_vectors[direction]
            c.setStrokeColorRGB(0, 0, 0)
            c.setLineWidth(2)
            c.line(cx + dx * radius, cy + dy * radius,
                   cx + dx * (radius + tail_len), cy + dy * (radius + tail_len))


def _draw_region_borders(c, puzzle, cell_size, x0, y0, thin_dashed=False):
    """Draw region borders (thick) and inner grid (thin)."""
    if thin_dashed:
        c.setStrokeColorRGB(0.5, 0.5, 0.5)
        c.setLineWidth(0.5)
        c.setDash(3, 3)
    else:
        c.setStrokeColorRGB(0.7, 0.7, 0.7)
        c.setLineWidth(0.5)
    for i in range(puzzle.rows + 1):
        y = y0 + i * cell_size
        c.line(x0, y, x0 + puzzle.cols * cell_size, y)
    for j in range(puzzle.cols + 1):
        x = x0 + j * cell_size
        c.line(x, y0, x, y0 + puzzle.rows * cell_size)
    if thin_dashed:
        c.setDash()
    c.setStrokeColorRGB(0, 0, 0)
    c.setLineWidth(2.5)
    c.rect(x0, y0, puzzle.cols * cell_size, puzzle.rows * cell_size, stroke=1, fill=0)
    for row, col in puzzle.vborders:
        x = x0 + (col + 1) * cell_size
        y_top = y0 + (puzzle.rows - row) * cell_size
        c.line(x, y_top - cell_size, x, y_top)
    for row, col in puzzle.hborders:
        y = y0 + (puzzle.rows - row - 1) * cell_size
        c.line(x0 + col * cell_size, y, x0 + (col + 1) * cell_size, y)


def render_mashu(c, puzzle):
    cell_size, x0, y0 = _calc_grid_params(puzzle, PAGE_W, PAGE_H)
    _draw_grid(c, puzzle.rows, puzzle.cols, cell_size, x0, y0)
    radius = cell_size * 0.32
    for row, col, val in puzzle.clues:
        cx, cy = _cell_center(row, col, puzzle.rows, cell_size, x0, y0)
        if val == 1:  # white circle
            c.setStrokeColorRGB(0, 0, 0)
            c.setFillColorRGB(1, 1, 1)
            c.setLineWidth(1.8)
            c.circle(cx, cy, radius, stroke=1, fill=1)
        elif val == 2:  # black circle
            c.setFillColorRGB(0, 0, 0)
            c.circle(cx, cy, radius, stroke=0, fill=1)


def render_simpleloop(c, puzzle):
    cell_size, x0, y0 = _calc_grid_params(puzzle, PAGE_W, PAGE_H)
    _draw_grid(c, puzzle.rows, puzzle.cols, cell_size, x0, y0)
    c.setFillColorRGB(0, 0, 0)
    for row, col in puzzle.blocked_cells:
        cx, cy = _cell_center(row, col, puzzle.rows, cell_size, x0, y0)
        c.rect(cx - cell_size / 2, cy - cell_size / 2,
               cell_size, cell_size, stroke=0, fill=1)


def render_starbattle(c, puzzle):
    cell_size, x0, y0 = _calc_grid_params(puzzle, PAGE_W, PAGE_H)
    _draw_region_borders(c, puzzle, cell_size, x0, y0)
    # Annotate the star count beneath the header
    c.setFont("Helvetica", 11)
    c.setFillColorRGB(0, 0, 0)
    label = f"{puzzle.star_count} star" + ("s" if puzzle.star_count != 1 else "")
    c.drawString(MARGIN, PAGE_H - MARGIN - 30, f"({label} per row, column, and region)")


def render_icelom(c, puzzle):
    cell_size, x0, y0 = _calc_grid_params(puzzle, PAGE_W, PAGE_H)
    _draw_grid(c, puzzle.rows, puzzle.cols, cell_size, x0, y0)
    # Ice cells (light blue)
    c.setFillColorRGB(0.8, 0.9, 1.0)
    for row, col in puzzle.ice:
        cx, cy = _cell_center(row, col, puzzle.rows, cell_size, x0, y0)
        c.rect(cx - cell_size / 2, cy - cell_size / 2,
               cell_size, cell_size, stroke=0, fill=1)
    c.setFillColorRGB(0, 0, 0)
    _draw_grid(c, puzzle.rows, puzzle.cols, cell_size, x0, y0)
    # Numbers in cells
    font_size = min(cell_size * 0.6, 20)
    c.setFont("Helvetica-Bold", font_size)
    for row, col, val in puzzle.clues:
        cx, cy = _cell_center(row, col, puzzle.rows, cell_size, x0, y0)
        c.drawCentredString(cx, cy - font_size * 0.3, str(val))
    # In/out arrows on the perimeter
    arrow_size = cell_size * 0.3
    for arrow_val, atype in [(puzzle.in_arrow, "in"), (puzzle.out_arrow, "out")]:
        cols, rows = puzzle.cols, puzzle.rows
        if arrow_val < cols:
            row, col, dr, dc = (-1 if atype == "in" else 0, arrow_val,
                                1 if atype == "in" else -1, 0)
        elif arrow_val < 2 * cols:
            row, col, dr, dc = (rows if atype == "in" else rows - 1, arrow_val - cols,
                                -1 if atype == "in" else 1, 0)
        elif arrow_val < 2 * cols + rows:
            row, col, dr, dc = (arrow_val - 2 * cols, -1 if atype == "in" else 0,
                                0, 1 if atype == "in" else -1)
        else:
            row, col, dr, dc = (arrow_val - 2 * cols - rows, cols if atype == "in" else cols - 1,
                                0, -1 if atype == "in" else 1)
        cx = x0 + (col + 0.5) * cell_size + (dc * cell_size * 0.5 if atype == "in" else 0)
        cy = y0 + (rows - row - 0.5) * cell_size - (dr * cell_size * 0.5 if atype == "in" else 0)
        if atype != "in":
            cx = x0 + (col + 0.5) * cell_size + dc * cell_size * 0.5
            cy = y0 + (rows - row - 0.5) * cell_size - dr * cell_size * 0.5
        _draw_arrow(c, cx, cy, dr, dc, arrow_size)


def render_barns(c, puzzle):
    cell_size, x0, y0 = _calc_grid_params(puzzle, PAGE_W, PAGE_H)
    # Ice cells background
    c.setFillColorRGB(0.8, 0.9, 1.0)
    for row, col in puzzle.ice:
        cx, cy = _cell_center(row, col, puzzle.rows, cell_size, x0, y0)
        c.rect(cx - cell_size / 2, cy - cell_size / 2,
               cell_size, cell_size, stroke=0, fill=1)
    c.setFillColorRGB(0, 0, 0)
    _draw_region_borders(c, puzzle, cell_size, x0, y0)


def render_reflect(c, puzzle):
    cell_size, x0, y0 = _calc_grid_params(puzzle, PAGE_W, PAGE_H)
    _draw_grid(c, puzzle.rows, puzzle.cols, cell_size, x0, y0)
    font_size = min(cell_size * 0.45, 14)
    for row, col, ques, val in puzzle.cells:
        cx, cy = _cell_center(row, col, puzzle.rows, cell_size, x0, y0)
        if ques == 0:
            # Block: solid black square
            c.setFillColorRGB(0, 0, 0)
            c.rect(cx - cell_size / 2, cy - cell_size / 2,
                   cell_size, cell_size, stroke=0, fill=1)
            continue
        # Mirror: triangle filling half the cell
        x = cx - cell_size / 2
        y = cy - cell_size / 2
        s = cell_size
        c.setFillColorRGB(0, 0, 0)
        p = c.beginPath()
        if ques == 2:  # ◣ bottom-left triangle
            p.moveTo(x, y); p.lineTo(x + s, y); p.lineTo(x, y + s)
        elif ques == 3:  # ◢ bottom-right triangle
            p.moveTo(x + s, y); p.lineTo(x + s, y + s); p.lineTo(x, y)
        elif ques == 4:  # ◤ top-left triangle
            p.moveTo(x, y + s); p.lineTo(x, y); p.lineTo(x + s, y + s)
        elif ques == 5:  # ◥ top-right triangle
            p.moveTo(x + s, y + s); p.lineTo(x, y + s); p.lineTo(x + s, y)
        p.close()
        c.drawPath(p, fill=1, stroke=0)
        # Number in the white half if present
        if val >= 0:
            # Place number in opposite corner from filled triangle
            off = cell_size * 0.28
            if ques == 2:
                tx, ty = cx + off, cy + off
            elif ques == 3:
                tx, ty = cx - off, cy + off
            elif ques == 4:
                tx, ty = cx + off, cy - off
            else:  # 5
                tx, ty = cx - off, cy - off
            c.setFillColorRGB(0, 0, 0)
            c.setFont("Helvetica-Bold", font_size)
            c.drawCentredString(tx, ty - font_size * 0.3, str(val))


def render_slalom(c, puzzle):
    cell_size, x0, y0 = _calc_grid_params(puzzle, PAGE_W, PAGE_H)
    _draw_grid(c, puzzle.rows, puzzle.cols, cell_size, x0, y0)
    font_size = min(cell_size * 0.4, 14)
    bar_w = cell_size * 0.18
    for entry in puzzle.cells:
        row, col, kind, num = entry
        cx, cy = _cell_center(row, col, puzzle.rows, cell_size, x0, y0)
        if kind == "block":
            # Black filled cell with optional white number
            c.setFillColorRGB(0, 0, 0)
            c.rect(cx - cell_size / 2, cy - cell_size / 2,
                   cell_size, cell_size, stroke=0, fill=1)
            if num is not None and num >= 0:
                c.setFillColorRGB(1, 1, 1)
                c.setFont("Helvetica-Bold", font_size)
                c.drawCentredString(cx, cy - font_size * 0.3, str(num))
        elif kind == "gate_v":
            # Vertical gate marker: bar on the left edge of the cell
            c.setFillColorRGB(0, 0, 0)
            c.rect(cx - cell_size / 2 - bar_w / 2, cy - cell_size * 0.45,
                   bar_w, cell_size * 0.9, stroke=0, fill=1)
        elif kind == "gate_h":
            # Horizontal gate marker: bar on the top edge of the cell
            c.setFillColorRGB(0, 0, 0)
            c.rect(cx - cell_size * 0.45, cy + cell_size / 2 - bar_w / 2,
                   cell_size * 0.9, bar_w, stroke=0, fill=1)
    # Start position: open circle in the cell
    if puzzle.start_row >= 0:
        cx, cy = _cell_center(puzzle.start_row, puzzle.start_col,
                              puzzle.rows, cell_size, x0, y0)
        c.setStrokeColorRGB(0, 0, 0)
        c.setFillColorRGB(1, 1, 1)
        c.setLineWidth(2)
        c.circle(cx, cy, cell_size * 0.32, stroke=1, fill=1)


def render_kinkonkan(c, puzzle):
    # Allocate margin around grid for edge clues
    available_w = PAGE_W - 2 * MARGIN
    available_h = PAGE_H - 2 * MARGIN - HEADER_HEIGHT
    # Reserve 1.2 cells worth of space on each side for the clues
    cell_size = min(available_w / (puzzle.cols + 2.4), available_h / (puzzle.rows + 2.4))
    grid_w = cell_size * puzzle.cols
    grid_h = cell_size * puzzle.rows
    x0 = MARGIN + (available_w - grid_w) / 2
    y_top = PAGE_H - MARGIN - HEADER_HEIGHT
    y0 = y_top - (available_h - grid_h) / 2 - grid_h
    _draw_region_borders(c, puzzle, cell_size, x0, y0)
    # Edge clues: letter + number
    font_size = min(cell_size * 0.32, 12)
    c.setFont("Helvetica-Bold", font_size)
    c.setFillColorRGB(0, 0, 0)
    for side, idx, letter_idx, val in puzzle.edge_clues:
        # Convert letter_idx (1-based) to letter sequence: 1=A, 2=B, ..., 26=Z, 27=AA, etc.
        letter = ""
        n = letter_idx
        while n > 0:
            n -= 1
            letter = chr(ord('A') + (n % 26)) + letter
            n //= 26
        num_text = "?" if val == -2 else str(val)
        text = f"{letter}{num_text}"
        if side == "top":
            tx = x0 + (idx + 0.5) * cell_size
            ty = y0 + grid_h + cell_size * 0.4
        elif side == "bottom":
            tx = x0 + (idx + 0.5) * cell_size
            ty = y0 - cell_size * 0.7
        elif side == "left":
            tx = x0 - cell_size * 0.6
            ty = y0 + (puzzle.rows - idx - 0.5) * cell_size - font_size * 0.3
        else:  # right
            tx = x0 + grid_w + cell_size * 0.6
            ty = y0 + (puzzle.rows - idx - 0.5) * cell_size - font_size * 0.3
        if side in ("top", "bottom"):
            c.drawCentredString(tx, ty, text)
        else:
            c.drawCentredString(tx, ty, text)


def render_shwolf(c, puzzle):
    cell_size, x0, y0 = _calc_grid_params(puzzle, PAGE_W, PAGE_H)
    _draw_grid(c, puzzle.rows, puzzle.cols, cell_size, x0, y0)
    # Cross dots on intersections
    dot_r = cell_size * 0.1
    c.setFillColorRGB(0, 0, 0)
    for cr, cc in puzzle.crosses:
        # cr in [0, rows-2], cc in [0, cols-2] — interior intersection
        x = x0 + (cc + 1) * cell_size
        y = y0 + (puzzle.rows - cr - 1) * cell_size
        c.circle(x, y, dot_r, stroke=0, fill=1)
    # Circles in cells: 1 = white (sheep), 2 = black (wolf)
    radius = cell_size * 0.3
    for row, col, val in puzzle.circles:
        cx, cy = _cell_center(row, col, puzzle.rows, cell_size, x0, y0)
        if val == 1:
            c.setStrokeColorRGB(0, 0, 0)
            c.setFillColorRGB(1, 1, 1)
            c.setLineWidth(1.5)
            c.circle(cx, cy, radius, stroke=1, fill=1)
        elif val == 2:
            c.setFillColorRGB(0, 0, 0)
            c.circle(cx, cy, radius, stroke=0, fill=1)


def render_wagiri(c, puzzle):
    """Wagiri: dashed grid + intersection circles (gokigen-style) + cell numbers."""
    cell_size = min((PAGE_W - 2 * MARGIN) / puzzle.cols,
                    (PAGE_H - 2 * MARGIN - HEADER_HEIGHT) / puzzle.rows)
    grid_w = cell_size * puzzle.cols
    grid_h = cell_size * puzzle.rows
    x0 = MARGIN + ((PAGE_W - 2 * MARGIN) - grid_w) / 2
    y_top = PAGE_H - MARGIN - HEADER_HEIGHT
    y0 = y_top - ((PAGE_H - 2 * MARGIN - HEADER_HEIGHT) - grid_h) / 2 - grid_h
    # Dashed grid
    c.setStrokeColorRGB(0.5, 0.5, 0.5)
    c.setLineWidth(0.5)
    c.setDash(3, 3)
    for i in range(puzzle.rows + 1):
        y = y0 + i * cell_size
        c.line(x0, y, x0 + puzzle.cols * cell_size, y)
    for j in range(puzzle.cols + 1):
        x = x0 + j * cell_size
        c.line(x, y0, x, y0 + puzzle.rows * cell_size)
    c.setDash()
    c.setStrokeColorRGB(0, 0, 0)
    c.setLineWidth(2)
    c.rect(x0, y0, puzzle.cols * cell_size, puzzle.rows * cell_size, stroke=1, fill=0)
    # Intersection circles with numbers
    radius = cell_size * 0.2
    cross_font = min(radius * 1.4, 14)
    for row, col, val in puzzle.cross_clues:
        ix = x0 + col * cell_size
        iy = y0 + (puzzle.rows - row) * cell_size
        c.setFillColorRGB(1, 1, 1)
        c.setStrokeColorRGB(0, 0, 0)
        c.setLineWidth(1.5)
        c.circle(ix, iy, radius, stroke=1, fill=1)
        if val != -2:
            c.setFillColorRGB(0, 0, 0)
            c.setFont("Helvetica-Bold", cross_font)
            c.drawCentredString(ix, iy - cross_font * 0.3, str(val))
    # Cell numbers
    cell_font = min(cell_size * 0.5, 18)
    c.setFont("Helvetica-Bold", cell_font)
    for row, col, val in puzzle.cell_clues:
        cx, cy = _cell_center(row, col, puzzle.rows, cell_size, x0, y0)
        text = "?" if val == -2 else str(val)
        c.setFillColorRGB(0, 0, 0)
        c.drawCentredString(cx, cy - cell_font * 0.3, text)


def render_unknown(c, puzzle):
    """Render a placeholder page for unsupported puzzle types."""
    c.setFont("Helvetica", 24)
    c.drawCentredString(PAGE_W / 2, PAGE_H / 2 + 20,
                        f"< {puzzle.puzzle_type} >")
    c.setFont("Helvetica-Oblique", 14)
    c.drawCentredString(PAGE_W / 2, PAGE_H / 2 - 10,
                        "watch this space")
    c.setFont("Helvetica", 10)
    c.drawCentredString(PAGE_W / 2, PAGE_H / 2 - 30,
                        f"{puzzle.cols} x {puzzle.rows}")


RENDERERS = {
    NurikabePuzzle: render_nurikabe,
    IceBarnPuzzle: render_icebarn,
    RegionPuzzle: render_region,
    RegionArrowPuzzle: render_region_arrow,
    DbchocoPuzzle: render_dbchoco,
    MidloopPuzzle: render_midloop,
    PipelinkPuzzle: render_pipelink,
    FireflyPuzzle: render_firefly,
    MashuPuzzle: render_mashu,
    SimpleLoopPuzzle: render_simpleloop,
    StarBattlePuzzle: render_starbattle,
    IcelomPuzzle: render_icelom,
    BarnsPuzzle: render_barns,
    ReflectPuzzle: render_reflect,
    SlalomPuzzle: render_slalom,
    KinkonkanPuzzle: render_kinkonkan,
    ShwolfPuzzle: render_shwolf,
    WagiriPuzzle: render_wagiri,
    UnknownPuzzle: render_unknown,
}


def render_front_page(c, year, month):
    """Render a title/front page."""
    month_name = calendar.month_name[month]
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(PAGE_W / 2, PAGE_H / 2 + 30, "Bachelor Seal Puzzles")
    c.setFont("Helvetica", 22)
    c.drawCentredString(PAGE_W / 2, PAGE_H / 2 - 10, f"{month_name} {year}")
    c.showPage()


def render_pdf(puzzles, output_path, year=None, month=None):
    """Render a list of Puzzle objects to a PDF file."""
    c = canvas.Canvas(output_path, pagesize=A4)

    if year and month:
        render_front_page(c, year, month)

    for puzzle in puzzles:
        _draw_header(c, puzzle, PAGE_W, PAGE_H)
        renderer = RENDERERS.get(type(puzzle), render_unknown)
        renderer(c, puzzle)
        c.showPage()

    c.save()
    page_count = len(puzzles) + (1 if year and month else 0)
    print(f"Wrote {page_count} pages to {output_path}")
