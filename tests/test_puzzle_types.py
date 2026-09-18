import unittest

from puzzle_types import get_type_module, supported_types
from puzzles import UnknownPuzzle, decode_puzzle


CASES = {
    "creek": (
        "http://pzv.jp/p.html?creek/10/10/"
        "h6bjbj6c2cdk1d6dk8di3322b766cdh2bkbh7diccg2dp",
        33,
    ),
    "nurimaze": (
        "http://pzv.jp/p.html?nurimaze/10/10/"
        "vrvvvrft7vfdpnftdvrelsrvvtnqdvvmvv6v53j3a4h471i273h4a3j45",
        10,
    ),
    "tateyoko": (
        "https://puzz.link/p?tateyoko/10/10/"
        "o1i211i22xi22npi43i32npi23i211i32i33npi23i2q1nri21i2p3n3n2i22n2i53ri63i3q1i22pn3i42np",
        38,
    ),
    "nuribou": (
        "http://pzv.jp/p.html?nuribou/10/10/j4k1l4u5h4s9t8iai2j8q5o",
        11,
    ),
}

KAKURO_254 = (
    "https://puzz.link/p?kakuro/11/11/"
    "00gjm04lf4l0Kn6fo7dlOcmO7qbgo00lOjmgalP0D0oCPo00KhlJAmKglEPoEJqhEmggl00o0Kn00l0gl0Dm0000JhDb3a7A3gEOg"
)


class PuzzleTypeTests(unittest.TestCase):
    def test_every_supported_type_has_a_complete_module(self):
        for puzzle_type in supported_types():
            with self.subTest(puzzle_type=puzzle_type):
                module = get_type_module(puzzle_type)
                self.assertIsNotNone(module)
                self.assertTrue(callable(module.decode))
                self.assertTrue(module.ENGLISH_NAME)
                self.assertTrue(module.RENDERER)
                self.assertGreaterEqual(len(module.RULES), 2)
                self.assertTrue(all(rule.strip() for rule in module.RULES))

    def test_new_2026_types_decode_without_placeholders(self):
        for puzzle_type, (url, clue_count) in CASES.items():
            with self.subTest(puzzle_type=puzzle_type):
                puzzle = decode_puzzle(url)
                self.assertNotIsInstance(puzzle, UnknownPuzzle)
                self.assertEqual(puzzle.puzzle_type, puzzle_type)
                self.assertEqual(len(puzzle.clues), clue_count)

    def test_nurimaze_contains_start_and_goal(self):
        puzzle = decode_puzzle(CASES["nurimaze"][0])
        symbols = {value for _row, _col, value in puzzle.clues}
        self.assertTrue({1, 2, 3, 4}.issubset(symbols))

    def test_tateyoko_preserves_block_cells(self):
        puzzle = decode_puzzle(CASES["tateyoko"][0])
        self.assertTrue(any(blocked for _row, _col, _value, blocked in puzzle.clues))

    def test_kakuro_decodes_runs_and_outside_clues(self):
        puzzle = decode_puzzle(KAKURO_254)

        self.assertIn((0, 1, 19, 16), puzzle.clue_cells)
        self.assertIn((2, 3, 12, 34), puzzle.clue_cells)
        self.assertIn((7, 6, 29, 24), puzzle.clue_cells)
        self.assertEqual(
            puzzle.edge_clues,
            [
                ("top", 2, 29), ("top", 3, 17), ("top", 4, 23),
                ("top", 6, 11), ("top", 7, 3), ("top", 9, 10),
                ("top", 10, 7), ("left", 3, 20), ("left", 4, 3),
                ("left", 5, 16), ("left", 8, 24), ("left", 9, 34),
                ("left", 10, 16),
            ],
        )


if __name__ == "__main__":
    unittest.main()
