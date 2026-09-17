# Bachelor Seal puzzle PDFs

This tool downloads the daily puzzles from the Bachelor Seal archive and
renders one printable PDF per month. Every puzzle page includes a compact rules
box beneath the grid.

Install the dependencies:

```sh
python -m pip install -r requirements.txt
```

Generate a single month:

```sh
python main.py 2026-09
```

Generate every available month in a year. For the current year this stops at
the current month, so a partial September archive is included automatically:

```sh
python main.py 2026
```

Use `-o DIRECTORY` with a year to place all PDFs in another directory. With a
single month, `-o FILE.pdf` selects that month's output file.

Puzzle-specific metadata and decoder selection live under `puzzle_types/`, one
module per puzz.link type. Shared binary codecs remain in `puzzles.py`, and
shared drawing routines remain in `renderer.py`.

Run the regression tests with:

```sh
python -m unittest discover -s tests
```
