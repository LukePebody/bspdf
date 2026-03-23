#!/usr/bin/env python3
"""Generate a PDF of Bachelor Seal puzzles for a given month."""

import argparse
import sys

from scraper import fetch_month
from puzzles import decode_puzzle
from renderer import render_pdf


def main():
    parser = argparse.ArgumentParser(
        description="Generate a PDF of Bachelor Seal puzzles for a given month."
    )
    parser.add_argument("month", help="Month in YYYY-MM format, e.g. 2026-02")
    parser.add_argument("-o", "--output", help="Output PDF path (default: YYYY-MM.pdf)")
    args = parser.parse_args()

    try:
        year, month = args.month.split("-")
        year, month = int(year), int(month)
    except ValueError:
        print(f"Invalid month format: {args.month!r}. Use YYYY-MM.", file=sys.stderr)
        sys.exit(1)

    output = args.output or f"{year:04d}-{month:02d}.pdf"

    print(f"Fetching puzzles for {year:04d}-{month:02d}...")
    posts = fetch_month(year, month)
    print(f"Found {len(posts)} posts with puzzle links.")

    if not posts:
        print("No puzzles found for this month.")
        sys.exit(0)

    puzzles = []
    for date, title, url, stars in posts:
        puzzle = decode_puzzle(url, title=title, date=date)
        puzzle.stars = stars
        puzzles.append(puzzle)
        status = puzzle.puzzle_type
        if hasattr(puzzle, 'clues'):
            status += f" ({len(puzzle.clues)} clues)"
        print(f"  {date} | {title} | {status}")

    render_pdf(puzzles, output, year=year, month=month)


if __name__ == "__main__":
    main()
