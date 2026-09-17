#!/usr/bin/env python3
"""Generate monthly PDFs of Bachelor Seal puzzles."""

import argparse
import datetime
from pathlib import Path

from puzzles import UnknownPuzzle, decode_puzzle
from renderer import render_pdf
from scraper import fetch_month


def generate_month(year, month, output):
    """Fetch, decode, and render one month; return its puzzle count."""
    label = f"{year:04d}-{month:02d}"
    print(f"Fetching puzzles for {label}...")
    posts = fetch_month(year, month)
    print(f"Found {len(posts)} posts with puzzle links.")

    if not posts:
        print("No puzzles found for this month.")
        return 0

    puzzles = []
    unknown_types = {}
    for date, title, url, stars in posts:
        puzzle = decode_puzzle(url, title=title, date=date)
        puzzle.stars = stars
        puzzles.append(puzzle)
        status = puzzle.puzzle_type
        if isinstance(puzzle, UnknownPuzzle):
            status += " [UNKNOWN]"
            unknown_types[puzzle.puzzle_type] = unknown_types.get(puzzle.puzzle_type, 0) + 1
        elif hasattr(puzzle, "clues"):
            status += f" ({len(puzzle.clues)} clues)"
        print(f"  {date} | {title} | {status}")

    if unknown_types:
        summary = ", ".join(
            f"{name} (x{count})" if count > 1 else name
            for name, count in sorted(unknown_types.items())
        )
        print(f"Unknown puzzle types: {summary}")

    output.parent.mkdir(parents=True, exist_ok=True)
    render_pdf(puzzles, str(output), year=year, month=month)
    return len(puzzles)


def _parse_period(value):
    """Parse YYYY or YYYY-MM and return a year and optional month."""
    parts = value.split("-")
    try:
        if len(parts) == 1 and len(parts[0]) == 4:
            return int(parts[0]), None
        if len(parts) == 2 and len(parts[0]) == 4 and len(parts[1]) == 2:
            year, month = map(int, parts)
            if 1 <= month <= 12:
                return year, month
    except ValueError:
        pass
    raise ValueError(f"Invalid period: {value!r}. Use YYYY or YYYY-MM.")


def main():
    parser = argparse.ArgumentParser(
        description=("Generate Bachelor Seal puzzle PDFs for one month, or for "
                     "every available month in a year.")
    )
    parser.add_argument("period", help="Year or month: YYYY or YYYY-MM")
    parser.add_argument(
        "-o", "--output",
        help=("Output PDF for a month, or output directory for a year "
              "(defaults to the current directory)"),
    )
    args = parser.parse_args()

    try:
        year, month = _parse_period(args.period)
    except ValueError as exc:
        parser.error(str(exc))

    if month is not None:
        output = Path(args.output or f"{year:04d}-{month:02d}.pdf")
        generate_month(year, month, output)
        return

    today = datetime.date.today()
    if year > today.year:
        parser.error(f"{year} is in the future")
    last_month = today.month if year == today.year else 12
    output_dir = Path(args.output or ".")
    total = 0
    for current_month in range(1, last_month + 1):
        output = output_dir / f"{year:04d}-{current_month:02d}.pdf"
        total += generate_month(year, current_month, output)
    print(f"Finished {last_month} month(s), {total} puzzles total.")


if __name__ == "__main__":
    main()
