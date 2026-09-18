"""Shared decoding building blocks used by the per-type modules."""

import math


def _args(puzzle_type, cols, rows, title, date, url):
    return dict(puzzle_type=puzzle_type, cols=cols, rows=rows,
                title=title, date=date, url=url)


def numbers(puzzle_type, cols, rows, data, title, date, url):
    import puzzles as p
    clues = p.decode_nurikabe(cols, rows, data)
    return p.NurikabePuzzle(**_args(puzzle_type, cols, rows, title, date, url),
                             clues=clues)


def number16(puzzle_type, cols, rows, data, title, date, url):
    import puzzles as p
    entries, _ = p.decode_number16(cols * rows, data)
    clues = [(idx // cols, idx % cols, val) for idx, val in entries]
    return p.NurikabePuzzle(**_args(puzzle_type, cols, rows, title, date, url),
                             clues=clues)


def number10(puzzle_type, cols, rows, data, title, date, url):
    import puzzles as p
    clues = []
    cell = 0
    for char in data:
        if cell >= cols * rows:
            break
        if char == ".":
            clues.append((cell // cols, cell % cols, -2))
            cell += 1
        elif "0" <= char <= "9":
            clues.append((cell // cols, cell % cols, int(char)))
            cell += 1
        elif "a" <= char <= "z":
            cell += int(char, 36) - 9
        else:
            cell += 1
    return p.NurikabePuzzle(**_args(puzzle_type, cols, rows, title, date, url),
                             clues=clues)


def regions(puzzle_type, cols, rows, data, title, date, url):
    import puzzles as p
    vborders, hborders, clues = p.decode_regions(cols, rows, data)
    return p.RegionPuzzle(**_args(puzzle_type, cols, rows, title, date, url),
                          vborders=vborders, hborders=hborders, clues=clues)


def room_regions(puzzle_type, cols, rows, data, title, date, url):
    import puzzles as p
    vborders, hborders, clues = p.decode_regions_roomclues(cols, rows, data)
    return p.RegionPuzzle(**_args(puzzle_type, cols, rows, title, date, url),
                          vborders=vborders, hborders=hborders, clues=clues)


def usoone_regions(puzzle_type, cols, rows, data, title, date, url):
    import puzzles as p
    vborders, hborders, clues = p.decode_regions_usoone(cols, rows, data)
    return p.RegionPuzzle(**_args(puzzle_type, cols, rows, title, date, url),
                          vborders=vborders, hborders=hborders, clues=clues)


def usoone_cells(puzzle_type, cols, rows, data, title, date, url):
    import puzzles as p
    clues = p.decode_usoone_clues(cols, rows, data, support_dot=True)
    return p.NurikabePuzzle(**_args(puzzle_type, cols, rows, title, date, url),
                             clues=clues)


def ringring(puzzle_type, cols, rows, data, title, date, url):
    import puzzles as p
    clues = [(row, col, -1) for row, col in p.decode_ringring(cols, rows, data)]
    return p.NurikabePuzzle(**_args(puzzle_type, cols, rows, title, date, url),
                             clues=clues)


def midloop(puzzle_type, cols, rows, data, title, date, url):
    import puzzles as p
    return p.MidloopPuzzle(**_args(puzzle_type, cols, rows, title, date, url),
                           dots=p.decode_midloop(cols, rows, data))


def pipelink(puzzle_type, cols, rows, data, title, date, url):
    import puzzles as p
    return p.PipelinkPuzzle(**_args(puzzle_type, cols, rows, title, date, url),
                            segments=p.decode_pipelink(cols, rows, data))


def gokigen(puzzle_type, cols, rows, data, title, date, url):
    import puzzles as p
    clues = p.decode_usoone_clues(cols + 1, rows + 1, data)
    return p.NurikabePuzzle(**_args(puzzle_type, cols, rows, title, date, url),
                             clues=clues)


def kuroclone(puzzle_type, cols, rows, data, title, date, url):
    import puzzles as p
    consumed = (math.ceil(rows * (cols - 1) / 5) +
                math.ceil((rows - 1) * cols / 5))
    vborders, hborders, _ = p.decode_regions(cols, rows, data)
    clues = p.decode_firefly(cols, rows, data[consumed:])
    return p.RegionArrowPuzzle(**_args(puzzle_type, cols, rows, title, date, url),
                               vborders=vborders, hborders=hborders, clues=clues)


def moonsun(puzzle_type, cols, rows, data, title, date, url):
    import puzzles as p
    consumed = (math.ceil(rows * (cols - 1) / 5) +
                math.ceil((rows - 1) * cols / 5))
    vborders, hborders, _ = p.decode_regions(cols, rows, data)
    entries, _ = p.decode_triple(cols * rows, data[consumed:])
    clues = [(idx // cols, idx % cols, val) for idx, val in entries]
    return p.RegionPuzzle(**_args(puzzle_type, cols, rows, title, date, url),
                          vborders=vborders, hborders=hborders, clues=clues)


def tapa(puzzle_type, cols, rows, data, title, date, url):
    import puzzles as p
    return p.NurikabePuzzle(**_args(puzzle_type, cols, rows, title, date, url),
                             clues=p.decode_tapa(cols, rows, data))


def sashigane(puzzle_type, cols, rows, data, title, date, url):
    import puzzles as p
    return p.FireflyPuzzle(**_args(puzzle_type, cols, rows, title, date, url),
                           clues=p.decode_sashigane(cols, rows, data))


def dbchoco(puzzle_type, cols, rows, data, title, date, url):
    import puzzles as p
    color_chars = math.ceil(cols * rows / 5)
    bits = []
    for char in data[:color_chars]:
        value = p.CHARS.index(char)
        bits.extend((value >> bit) & 1 for bit in range(4, -1, -1))
    grey_cells = [(idx // cols, idx % cols)
                  for idx in range(cols * rows) if bits[idx]]
    clues = p.decode_nurikabe(cols, rows, data[color_chars:])
    return p.DbchocoPuzzle(**_args(puzzle_type, cols, rows, title, date, url),
                           grey_cells=grey_cells, clues=clues)


def firefly(puzzle_type, cols, rows, data, title, date, url):
    import puzzles as p
    return p.FireflyPuzzle(**_args(puzzle_type, cols, rows, title, date, url),
                           clues=p.decode_firefly(cols, rows, data))


def icebarn(puzzle_type, cols, rows, data, title, date, url):
    import puzzles as p
    ice, arrows, in_arrow, out_arrow = p.decode_icebarn(cols, rows, data)
    return p.IceBarnPuzzle(**_args(puzzle_type, cols, rows, title, date, url),
                           ice=ice, arrows=arrows,
                           in_arrow=in_arrow, out_arrow=out_arrow)


def mashu(puzzle_type, cols, rows, data, title, date, url):
    import puzzles as p
    entries, _ = p.decode_triple(cols * rows, data)
    clues = [(idx // cols, idx % cols, val) for idx, val in entries]
    return p.MashuPuzzle(**_args(puzzle_type, cols, rows, title, date, url),
                         clues=clues)


def fivecells(puzzle_type, cols, rows, data, title, date, url):
    import puzzles as p
    clues = []
    cell = 0
    for char in data:
        if cell >= cols * rows:
            break
        if char == "7":
            clues.append((cell // cols, cell % cols, -3))
            cell += 1
        elif char == ".":
            clues.append((cell // cols, cell % cols, -2))
            cell += 1
        elif "0" <= char <= "9":
            clues.append((cell // cols, cell % cols, int(char)))
            cell += 1
        elif "a" <= char <= "z":
            cell += int(char, 36) - 9
        else:
            cell += 1
    return p.NurikabePuzzle(**_args(puzzle_type, cols, rows, title, date, url),
                             clues=clues)


def room_numbers(puzzle_type, cols, rows, data, title, date, url):
    import puzzles as p
    vborders, hborders, consumed = p.decode_borders_only(cols, rows, data)
    room_tops = p._find_room_top_cells(cols, rows, vborders, hborders)
    entries, _ = p.decode_number16(len(room_tops), data[consumed:])
    clues = [(room_tops[idx][0], room_tops[idx][1], val)
             for idx, val in entries]
    return p.RegionPuzzle(**_args(puzzle_type, cols, rows, title, date, url),
                          vborders=vborders, hborders=hborders, clues=clues)


def cbblock(puzzle_type, cols, rows, data, title, date, url):
    import puzzles as p
    vertical_count = rows * (cols - 1)
    horizontal_count = (rows - 1) * cols
    bits = []
    for char in data[:math.ceil((vertical_count + horizontal_count) / 5)]:
        try:
            value = int(char, 32)
        except ValueError:
            value = 0
        bits.extend(1 if value & weight else 0 for weight in (16, 8, 4, 2, 1))
    vborders = [(idx // (cols - 1), idx % (cols - 1))
                for idx in range(vertical_count) if bits[idx]]
    hborders = [(idx // cols, idx % cols) for idx in range(horizontal_count)
                if bits[vertical_count + idx]]
    return p.CbblockPuzzle(**_args(puzzle_type, cols, rows, title, date, url),
                           vborders=vborders, hborders=hborders)


def _cross_marks(cols, rows, data):
    cross_cols = cols - 1
    count = cross_cols * (rows - 1)
    crosses = []
    position = 0
    offset = 0
    while offset < len(data) and position < count:
        char = data[offset]
        if char.isalnum():
            position += int(char, 36)
            if position < count:
                crosses.append((position // cross_cols, position % cross_cols))
            position += 1
        elif char == ".":
            position += 35
        offset += 1
    return crosses, offset


def bdblock(puzzle_type, cols, rows, data, title, date, url):
    import puzzles as p
    crosses, consumed = _cross_marks(cols, rows, data)
    rest = data[consumed:]
    if rest.startswith("/"):
        rest = rest[1:]
    entries, _ = p.decode_number16(cols * rows, rest)
    clues = [(idx // cols, idx % cols, val) for idx, val in entries]
    return p.BdblockPuzzle(**_args(puzzle_type, cols, rows, title, date, url),
                           crosses=crosses, clues=clues)


def kakuro(puzzle_type, cols, rows, data, title, date, url):
    import puzzles as p

    def value(char):
        if "0" <= char <= "9":
            return int(char)
        if "a" <= char <= "j":
            return int(char, 36)
        if "A" <= char <= "Z":
            return int(char, 36) + 10
        return -1

    clue_cells = []
    cell = offset = 0
    while offset < len(data) and cell < cols * rows:
        char = data[offset]
        if "k" <= char <= "z":
            # k-z encode runs of 1-16 ordinary (white) cells.
            cell += int(char, 36) - 19
            offset += 1
        elif char == ".":
            clue_cells.append((cell // cols, cell % cols, -1, -1))
            cell += 1
            offset += 1
        else:
            # Puzz.link stores the down clue first and the across clue second.
            down = value(char)
            across = value(data[offset + 1]) if offset + 1 < len(data) else -1
            clue_cells.append((cell // cols, cell % cols, across, down))
            cell += 1
            offset += 2

    # Kakuro's top and left clue bands are ExCells in pzpr.js. Their values
    # follow the in-grid data, first across the top and then down the left,
    # with no value encoded where the adjacent in-grid cell is itself a clue.
    clue_positions = {(row, col) for row, col, _across, _down in clue_cells}
    edge_clues = []
    for col in range(cols):
        if (0, col) not in clue_positions and offset < len(data):
            edge_clues.append(("top", col, value(data[offset])))
            offset += 1
    for row in range(rows):
        if (row, 0) not in clue_positions and offset < len(data):
            edge_clues.append(("left", row, value(data[offset])))
            offset += 1

    return p.KakuroPuzzle(**_args(puzzle_type, cols, rows, title, date, url),
                          clue_cells=clue_cells, edge_clues=edge_clues)


def wagiri(puzzle_type, cols, rows, data, title, date, url):
    import puzzles as p
    cross_clues = []
    position = offset = 0
    cross_count = (cols + 1) * (rows + 1)
    while offset < len(data) and position < cross_count:
        char = data[offset]
        if "0" <= char <= "4":
            cross_clues.append((position // (cols + 1), position % (cols + 1), int(char)))
            position += 1
        elif "5" <= char <= "9":
            cross_clues.append((position // (cols + 1), position % (cols + 1), int(char) - 5))
            position += 2
        elif "a" <= char <= "e":
            cross_clues.append((position // (cols + 1), position % (cols + 1), int(char, 16) - 10))
            position += 3
        elif "g" <= char <= "z":
            position += int(char, 36) - 15
        elif char == ".":
            cross_clues.append((position // (cols + 1), position % (cols + 1), -2))
            position += 1
        else:
            position += 1
        offset += 1
    rest = data[offset:]
    cell_clues = []
    position = 0
    for char in rest:
        if position >= cols * rows:
            break
        if char == ".":
            cell_clues.append((position // cols, position % cols, -2))
            position += 1
        elif "0" <= char <= "9":
            cell_clues.append((position // cols, position % cols, int(char)))
            position += 1
        elif "a" <= char <= "z":
            position += int(char, 36) - 9
        else:
            position += 1
    return p.WagiriPuzzle(**_args(puzzle_type, cols, rows, title, date, url),
                          cross_clues=cross_clues, cell_clues=cell_clues)


def akari(puzzle_type, cols, rows, data, title, date, url):
    import puzzles as p
    clues = p.decode_usoone_clues(cols, rows, data, support_dot=True)
    return p.NurikabePuzzle(**_args("akari", cols, rows, title, date, url),
                             clues=clues)


def shugaku(puzzle_type, cols, rows, data, title, date, url):
    import puzzles as p
    clues = []
    cell = 0
    for char in data:
        if cell >= cols * rows:
            break
        if "0" <= char <= "4":
            clues.append((cell // cols, cell % cols, int(char)))
            cell += 1
        elif char == "5":
            clues.append((cell // cols, cell % cols, -2))
            cell += 1
        else:
            cell += int(char, 36) - 5
    return p.NurikabePuzzle(**_args(puzzle_type, cols, rows, title, date, url),
                             clues=clues)


def simpleloop(puzzle_type, cols, rows, data, title, date, url):
    import puzzles as p
    blocked, _ = p.decode_binary(cols * rows, data)
    cells = [(idx // cols, idx % cols) for idx in blocked]
    return p.SimpleLoopPuzzle(**_args(puzzle_type, cols, rows, title, date, url),
                              blocked_cells=cells)


def starbattle(puzzle_type, cols, rows, data, title, date, url):
    import puzzles as p
    parts = data.split("/")
    count = int(parts[0]) if parts and parts[0].isdigit() else 1
    vborders, hborders, _ = p.decode_regions(cols, rows, "/".join(parts[1:]))
    return p.StarBattlePuzzle(**_args(puzzle_type, cols, rows, title, date, url),
                              vborders=vborders, hborders=hborders,
                              star_count=count)


def yajikazu(puzzle_type, cols, rows, data, title, date, url):
    import puzzles as p
    entries, _ = p.decode_arrow_number16(cols * rows, data)
    clues = []
    for idx, direction, number in entries:
        row, col = divmod(idx, cols)
        if number == -3:
            clues.append((row, col, 0, None))
        else:
            clues.append((row, col, direction, None if number == -2 else number))
    return p.FireflyPuzzle(**_args(puzzle_type, cols, rows, title, date, url),
                           clues=clues)


def icelom(puzzle_type, cols, rows, data, title, date, url):
    import puzzles as p
    ice_indices, consumed = p.decode_binary(cols * rows, data)
    ice = [(idx // cols, idx % cols) for idx in ice_indices]
    rest = data[consumed:]
    entries, number_chars = p.decode_number16(cols * rows, rest)
    clues = [(idx // cols, idx % cols, val) for idx, val in entries]
    in_arrow = out_arrow = 0
    tail = rest[number_chars:]
    if tail.startswith("/"):
        parts = tail[1:].split("/")
        if parts and parts[0].isdigit():
            in_arrow = int(parts[0])
        if len(parts) > 1 and parts[1].isdigit():
            out_arrow = int(parts[1])
    return p.IcelomPuzzle(**_args(puzzle_type, cols, rows, title, date, url),
                          ice=ice, clues=clues,
                          in_arrow=in_arrow, out_arrow=out_arrow)


def barns(puzzle_type, cols, rows, data, title, date, url):
    import puzzles as p
    ice_indices, consumed = p.decode_binary(cols * rows, data)
    ice = [(idx // cols, idx % cols) for idx in ice_indices]
    vborders, hborders, _ = p.decode_regions(cols, rows, data[consumed:])
    return p.BarnsPuzzle(**_args(puzzle_type, cols, rows, title, date, url),
                         ice=ice, vborders=vborders, hborders=hborders)


def reflect(puzzle_type, cols, rows, data, title, date, url):
    import puzzles as p
    cells = []
    cell = offset = 0
    while offset < len(data) and cell < cols * rows:
        char = data[offset]
        if char == "5":
            cells.append((cell // cols, cell % cols, 0, -1))
            cell += 1
            offset += 1
        elif "1" <= char <= "4":
            value = int(data[offset + 1], 16)
            cells.append((cell // cols, cell % cols, int(char) + 1,
                          -1 if value == 0 else value))
            cell += 1
            offset += 2
        elif "6" <= char <= "9":
            value = int(data[offset + 1:offset + 3], 16)
            cells.append((cell // cols, cell % cols, int(char) - 4,
                          -1 if value == 0 else value))
            cell += 1
            offset += 3
        elif "a" <= char <= "z":
            cell += int(char, 36) - 9
            offset += 1
        else:
            offset += 1
    return p.ReflectPuzzle(**_args(puzzle_type, cols, rows, title, date, url),
                           cells=cells)


def slalom(puzzle_type, cols, rows, data, title, date, url):
    import puzzles as p
    parts = data.split("/")
    body = parts[0]
    start_index = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else -1
    blocks = []
    gates = []
    cell = offset = 0
    while offset < len(body) and cell < cols * rows:
        char = body[offset]
        if char == "1":
            blocks.append((cell // cols, cell % cols))
            cell += 1
        elif char == "2":
            gates.append((cell // cols, cell % cols, "gate_v"))
            cell += 1
        elif char == "3":
            gates.append((cell // cols, cell % cols, "gate_h"))
            cell += 1
        elif "4" <= char <= "9" or "a" <= char <= "z":
            cell += int(char, 36) - 3
        offset += 1
    numbers = {}
    block_index = 0
    while offset < len(body) and block_index < len(blocks):
        char = body[offset]
        if char in "0123456789abcdef":
            numbers[block_index] = int(char, 16)
            block_index += 1
            offset += 1
        elif char == "-":
            numbers[block_index] = int(body[offset + 1:offset + 3], 16)
            block_index += 1
            offset += 3
        elif char == ".":
            numbers[block_index] = -2
            block_index += 1
            offset += 1
        else:
            offset += 1
    cells = [(row, col, "block", numbers.get(idx))
             for idx, (row, col) in enumerate(blocks)]
    cells.extend((row, col, kind, None) for row, col, kind in gates)
    start_row, start_col = (-1, -1)
    if 0 <= start_index < cols * rows:
        start_row, start_col = divmod(start_index, cols)
    return p.SlalomPuzzle(**_args(puzzle_type, cols, rows, title, date, url),
                          cells=cells, start_row=start_row, start_col=start_col)


def kinkonkan(puzzle_type, cols, rows, data, title, date, url):
    import puzzles as p
    vborders, hborders, consumed = p.decode_borders_only(cols, rows, data)
    rest = data[consumed:]
    edge_count = 2 * (cols + rows)
    positions = []
    letters = {}
    edge = offset = 0
    while offset < len(rest) and edge < edge_count:
        char = rest[offset]
        if "A" <= char <= "Z":
            letters[edge] = int(char, 36) - 9
            positions.append(edge)
            edge += 1
            offset += 1
        elif "0" <= char <= "9" and offset + 1 < len(rest):
            letters[edge] = int(rest[offset + 1], 36) - 9 + (int(char) + 1) * 26
            positions.append(edge)
            edge += 1
            offset += 2
        elif "a" <= char <= "z":
            edge += int(char, 36) - 9
            offset += 1
        else:
            offset += 1
    numbers = {}
    for edge_id in positions:
        if offset >= len(rest):
            break
        char = rest[offset]
        if char == ".":
            numbers[edge_id] = -2
            offset += 1
        elif char == "-":
            numbers[edge_id] = int(rest[offset + 1:offset + 3], 16)
            offset += 3
        else:
            numbers[edge_id] = int(char, 16)
            offset += 1
    edge_clues = []
    for edge_id, letter in letters.items():
        if edge_id < cols:
            side, idx = "top", edge_id
        elif edge_id < 2 * cols:
            side, idx = "bottom", edge_id - cols
        elif edge_id < 2 * cols + rows:
            side, idx = "left", edge_id - 2 * cols
        else:
            side, idx = "right", edge_id - 2 * cols - rows
        edge_clues.append((side, idx, letter, numbers.get(edge_id, -2)))
    return p.KinkonkanPuzzle(**_args(puzzle_type, cols, rows, title, date, url),
                             vborders=vborders, hborders=hborders,
                             edge_clues=edge_clues)


def shwolf(puzzle_type, cols, rows, data, title, date, url):
    import puzzles as p
    crosses, consumed = _cross_marks(cols, rows, data)
    entries, _ = p.decode_triple(cols * rows, data[consumed:])
    circles = [(idx // cols, idx % cols, val) for idx, val in entries]
    return p.ShwolfPuzzle(**_args(puzzle_type, cols, rows, title, date, url),
                          crosses=crosses, circles=circles)


def creek(puzzle_type, cols, rows, data, title, date, url):
    import puzzles as p
    clues = p.decode_usoone_clues(cols + 1, rows + 1, data, support_dot=True)
    return p.NurikabePuzzle(**_args(puzzle_type, cols, rows, title, date, url),
                             clues=clues)


def nurimaze(puzzle_type, cols, rows, data, title, date, url):
    import puzzles as p
    vborders, hborders, consumed = p.decode_borders_only(cols, rows, data)
    clues = []
    cell = 0
    for char in data[consumed:]:
        if cell >= cols * rows:
            break
        if char in "1234":
            clues.append((cell // cols, cell % cols, int(char)))
        elif "5" <= char <= "9" or "a" <= char <= "z":
            cell += int(char, 36) - 5
        cell += 1
    return p.RegionPuzzle(**_args(puzzle_type, cols, rows, title, date, url),
                          vborders=vborders, hborders=hborders, clues=clues)


def tateyoko(puzzle_type, cols, rows, data, title, date, url):
    import puzzles as p
    clues = []
    cell = offset = 0
    while offset < len(data) and cell < cols * rows:
        char = data[offset]
        blocked = False
        value = None
        if char == ".":
            value = -2
        elif char == "x":
            blocked = True
        elif "o" <= char <= "s":
            blocked = True
            value = int(char, 29) - 24
        elif char in "0123456789abcdef":
            value = int(char, 16)
        elif char == "-":
            value = int(data[offset + 1:offset + 3], 16)
            offset += 2
        elif char == "i" and offset + 1 < len(data):
            cell += int(data[offset + 1], 16) - 1
            offset += 1
        if blocked or value is not None:
            clues.append((cell // cols, cell % cols, value, blocked))
        cell += 1
        offset += 1
    return p.TateyokoPuzzle(**_args(puzzle_type, cols, rows, title, date, url),
                            clues=clues)
