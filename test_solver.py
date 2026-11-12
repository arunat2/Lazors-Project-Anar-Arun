"""Simple checks for the Lazors program.

Run from the project folder: python3 -m unittest -v test_solver
Each test sets up a small example and checks its expected result.
"""

import tempfile
import unittest
from pathlib import Path

from LazorGroupProjectAnarArun import (
    Block,
    Board,
    generate_placements,
    read_bff,
    simulate_lasers,
    solve_board,
    write_solution,
)


class SolverTests(unittest.TestCase):
    """Check block behavior, placements, solving, and output."""

    def test_reflective_block(self):
        """A vertical face reverses x; a horizontal face reverses y."""
        block = Block("A")
        self.assertEqual(block.hit(1, -1, "vertical"), [(-1, -1)])
        self.assertEqual(block.hit(1, -1, "horizontal"), [(1, 1)])

    def test_opaque_block(self):
        """An opaque block stops the beam."""
        block = Block("B")
        self.assertEqual(block.hit(1, -1, "vertical"), [])

    def test_refractive_block(self):
        """A refractive block transmits one beam and reflects another."""
        block = Block("C")
        self.assertEqual(block.hit(1, -1, "vertical"),
                         [(1, -1), (-1, -1)])

    def test_placements(self):
        """Two identical blocks in three spaces give three arrangements."""
        board = Board()
        board.grid = [["o", "o", "o"]]
        board.blocks["A"] = 2

        arrangements = []
        for grid in generate_placements(board):
            row = []
            for cell in grid[0]:
                if isinstance(cell, Block):
                    row.append(cell.kind)
                else:
                    row.append(cell)
            arrangements.append(row)

        self.assertEqual(arrangements,
                         [["A", "A", "o"],
                          ["A", "o", "A"],
                          ["o", "A", "A"]])
        # Trying placements must not change the original board.
        self.assertEqual(board.grid, [["o", "o", "o"]])

    def test_fixed_block_and_forbidden_space(self):
        """Only the empty allowed space can receive the movable block."""
        board = Board()
        fixed_block = Block("C", True)
        board.grid = [[fixed_block, "x", "o"]]
        board.blocks["A"] = 1

        arrangements = list(generate_placements(board))
        self.assertEqual(len(arrangements), 1)
        grid = arrangements[0]
        self.assertIs(grid[0][0], fixed_block)
        self.assertEqual(grid[0][1], "x")
        self.assertEqual(grid[0][2].kind, "A")

    def test_find_solution(self):
        """The reflective block must go on the left to reach the target."""
        board = Board()
        board.grid = [["o", "o"]]
        board.blocks["A"] = 1
        board.lasers = [(2, 1, -1, -1)]
        board.targets = [(3, 0)]

        solution = solve_board(board)
        self.assertIsNotNone(solution)
        self.assertEqual(solution[0][0].kind, "A")
        self.assertEqual(solution[0][1], "o")
        reached = simulate_lasers(board, solution)
        self.assertIn((3, 0), reached)

    def test_no_solution(self):
        """An opaque block in the only space prevents reaching the target."""
        board = Board()
        board.grid = [["o"]]
        board.blocks["B"] = 1
        board.lasers = [(0, 1, 1, -1)]
        board.targets = [(1, 0)]

        self.assertIsNone(solve_board(board))

    def test_save_solution(self):
        """Save a solution and check that it loads as the same solved board."""
        board = Board()
        board.grid = [["o", "o"]]
        board.blocks["A"] = 1
        board.lasers = [(2, 1, -1, -1)]
        board.targets = [(3, 0)]
        solution = solve_board(board)
        self.assertIsNotNone(solution)

        # A temporary folder keeps test files out of the project.
        # Python removes it automatically when this section finishes.
        with tempfile.TemporaryDirectory() as folder:
            filename = Path(folder) / "solution.bff"
            write_solution(board, solution, filename)
            saved_board = read_bff(filename)

            self.assertEqual(saved_board.grid[0][0].kind, "A")
            self.assertTrue(saved_board.grid[0][0].fixed)
            self.assertEqual(saved_board.grid[0][1], "o")
            self.assertEqual(saved_board.blocks, {"A": 0, "B": 0, "C": 0})
            self.assertEqual(saved_board.lasers, board.lasers)
            self.assertEqual(saved_board.targets, board.targets)
            reached = simulate_lasers(saved_board)
            self.assertIn((3, 0), reached)


if __name__ == "__main__":
    unittest.main()
