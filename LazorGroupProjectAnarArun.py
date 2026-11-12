"""Read a Lazors board, find a solution, and save it."""

from itertools import combinations
from pathlib import Path
import sys


class Block:
    """Store one block."""

    def __init__(self, kind, fixed=False):
        """Save the block information."""
        self.kind = kind
        self.fixed = fixed

    def hit(self, dx, dy, side):
        """Find where the laser goes."""
        if side == "vertical":
            new_dx = -dx
            new_dy = dy
        else:
            new_dx = dx
            new_dy = -dy

        if self.kind == "A":
            return [(new_dx, new_dy)]

        if self.kind == "B":
            return []

        # C makes two beams.
        return [(dx, dy), (new_dx, new_dy)]


class Board:
    """Store the board information."""

    def __init__(self):
        """Start with empty values."""
        self.grid = []
        self.blocks = {"A": 0, "B": 0, "C": 0}
        self.lasers = []
        self.targets = []


def read_bff(filename):
    """Read the puzzle file."""
    board = Board()
    reading_grid = False
    grid_started = False
    grid_finished = False

    with open(filename, "r") as file:
        for line in file:
            # Remove comments.
            line = line.split("#")[0]
            line = line.strip()

            if line == "":
                continue

            if line == "GRID START":
                if grid_started:
                    raise ValueError("The grid was started twice.")

                reading_grid = True
                grid_started = True

            elif line == "GRID STOP":
                if not reading_grid:
                    raise ValueError("The grid has not started.")

                reading_grid = False
                grid_finished = True

            elif reading_grid:
                row = []
                symbols = line.split()

                for symbol in symbols:
                    if symbol == "o" or symbol == "x":
                        row.append(symbol)

                    elif symbol in ("A", "B", "C"):
                        row.append(Block(symbol, True))

                    else:
                        raise ValueError("Unknown grid symbol.")

                board.grid.append(row)

            else:
                parts = line.split()
                letter = parts[0]

                if letter in ("A", "B", "C"):
                    if len(parts) != 2:
                        raise ValueError("A block count needs two values.")

                    count = int(parts[1])

                    if count < 0:
                        raise ValueError("A block count cannot be negative.")

                    board.blocks[letter] += count

                elif letter == "L":
                    if len(parts) != 5:
                        raise ValueError("A laser needs four numbers.")

                    x = int(parts[1])
                    y = int(parts[2])
                    dx = int(parts[3])
                    dy = int(parts[4])

                    board.lasers.append((x, y, dx, dy))

                elif letter == "P":
                    if len(parts) != 3:
                        raise ValueError("A target needs two numbers.")

                    x = int(parts[1])
                    y = int(parts[2])

                    board.targets.append((x, y))

                else:
                    raise ValueError("Unknown line in the file.")

    check_board(board, grid_finished)
    return board


def check_board(board, grid_finished):
    """Check the information from the file."""
    if not grid_finished or len(board.grid) == 0:
        raise ValueError("The file needs a complete grid.")

    height = len(board.grid)
    width = len(board.grid[0])
    spaces = 0

    for row in board.grid:
        if len(row) != width:
            raise ValueError("The rows must have the same length.")

        for cell in row:
            if cell == "o":
                spaces += 1

    total_blocks = 0

    for kind in board.blocks:
        total_blocks += board.blocks[kind]

    if total_blocks > spaces:
        raise ValueError("There are too many blocks for the board.")

    if len(board.lasers) == 0 or len(board.targets) == 0:
        raise ValueError("The board needs a laser and a target.")

    for x, y, dx, dy in board.lasers:
        if dx not in (-1, 1) or dy not in (-1, 1):
            raise ValueError("Laser directions must be 1 or -1.")

        check_point(x, y, width, height)

    for x, y in board.targets:
        check_point(x, y, width, height)


def check_point(x, y, width, height):
    """Check a laser or target position."""
    if x < 0 or x > 2 * width:
        raise ValueError("An x position is outside the board.")

    if y < 0 or y > 2 * height:
        raise ValueError("A y position is outside the board.")

    if (x + y) % 2 != 1:
        raise ValueError("Positions must be at block edge midpoints.")


def simulate_lasers(board, grid=None):
    """Return the points reached by the lasers."""
    if grid is None:
        grid = board.grid

    height = len(board.grid)
    width = len(board.grid[0])

    if len(grid) != height:
        raise ValueError("The grid height cannot change.")

    for row in grid:
        if len(row) != width:
            raise ValueError("The grid width cannot change.")

    # Check fixed blocks and blocked spaces.
    for row in range(height):
        for column in range(width):
            original = board.grid[row][column]
            cell = grid[row][column]

            if isinstance(cell, Block):
                if cell.kind not in ("A", "B", "C"):
                    raise ValueError("Unknown block type.")
            elif cell not in ("o", "x"):
                raise ValueError("Unknown grid symbol.")

            if original == "x" and cell != "x":
                raise ValueError("An x space cannot change.")

            if isinstance(original, Block):
                if original.fixed:
                    if not isinstance(cell, Block):
                        raise ValueError("A fixed block was removed.")

                    if cell.kind != original.kind:
                        raise ValueError("A fixed block was changed.")

    beams = []
    visited = set()
    reached = set()

    for laser in board.lasers:
        beams.append(laser)

    while len(beams) > 0:
        x, y, dx, dy = beams.pop()

        if x < 0 or x > 2 * width:
            continue

        if y < 0 or y > 2 * height:
            continue

        # This stops repeated paths.
        state = (x, y, dx, dy)

        if state in visited:
            continue

        visited.add(state)
        reached.add((x, y))

        # Find the cell ahead.
        if x % 2 == 0:
            side = "vertical"
            row = y // 2
            column = x // 2

            if dx == -1:
                column -= 1

        else:
            side = "horizontal"
            row = y // 2
            column = x // 2

            if dy == -1:
                row -= 1

        if row < 0 or row >= height:
            continue

        if column < 0 or column >= width:
            continue

        cell = grid[row][column]

        if isinstance(cell, Block):
            directions = cell.hit(dx, dy, side)
        else:
            directions = [(dx, dy)]

        # Move each beam one step.
        for new_dx, new_dy in directions:
            next_x = x + new_dx
            next_y = y + new_dy

            beams.append((next_x, next_y, new_dx, new_dy))

    return reached


# Solver and output functions.
def generate_placements(board):
    """Yield each unique placement, using every available movable block."""
    spaces = []
    for row in range(len(board.grid)):
        for column in range(len(board.grid[row])):
            if board.grid[row][column] == "o":
                spaces.append((row, column))

    # Copy rows so the original board stays unchanged.
    grid = [row[:] for row in board.grid]
    kinds = ["A", "B", "C"]

    def place_kind(index, remaining):
        """Choose positions for one kind, then place the next kind."""
        if index == len(kinds):
            yield [row[:] for row in grid]
            return

        kind = kinds[index]
        count = board.blocks[kind]
        # Combinations avoid swapping identical blocks into duplicate boards.
        for chosen in combinations(remaining, count):
            for row, column in chosen:
                grid[row][column] = Block(kind)

            next_spaces = []
            for position in remaining:
                if position not in chosen:
                    next_spaces.append(position)

            yield from place_kind(index + 1, next_spaces)

            for row, column in chosen:
                grid[row][column] = "o"

    yield from place_kind(0, spaces)


def solve_board(board):
    """Return the first solution grid, or None if no arrangement works."""
    for grid in generate_placements(board):
        reached = simulate_lasers(board, grid)
        if all(target in reached for target in board.targets):
            return grid
    return None


def write_solution(board, grid, filename):
    """Save the solved layout in readable, reusable BFF format."""
    # All placed blocks are fixed in the saved solution. The remaining
    # movable counts are zero, so read_bff can load this board again.
    with open(filename, "w") as file:
        file.write("# Solved Lazors board; all shown blocks are fixed.\n")
        file.write("# A = reflect, B = opaque, C = refract\n")
        file.write("# o = empty allowed space, x = no block allowed\n")
        file.write("GRID START\n")
        for row in grid:
            symbols = []
            for cell in row:
                if isinstance(cell, Block):
                    symbols.append(cell.kind)
                else:
                    symbols.append(cell)
            file.write(" ".join(symbols) + "\n")
        file.write("GRID STOP\nA 0\nB 0\nC 0\n")
        for x, y, dx, dy in board.lasers:
            file.write(f"L {x} {y} {dx} {dy}\n")
        for x, y in board.targets:
            file.write(f"P {x} {y}\n")


def main():
    """Read a puzzle, solve it, and report where the result was saved."""
    if len(sys.argv) > 3:
        print("Usage: python LazorGroupProjectAnarArun.py [puzzle.bff] [output.bff]")
        return 1

    try:
        if len(sys.argv) >= 2:
            filename = sys.argv[1]
        else:
            filename = input("Enter the .bff filename: ").strip()

        if len(sys.argv) == 3:
            output = Path(sys.argv[2])
        else:
            path = Path(filename)
            output = path.with_name(path.stem + "_solution.bff")

        if Path(filename).resolve() == output.resolve():
            raise ValueError("The output filename must differ from the puzzle.")
        if output.exists():
            raise ValueError("The output file already exists. Choose a new name.")

        board = read_bff(filename)
        solution = solve_board(board)
        if solution is None:
            print("No solution found. No output file was written.")
            return 0

        write_solution(board, solution, output)
        print("Solution found. All targets were reached.")
        print("Solution saved to:", output)
        return 0

    except (OSError, ValueError, EOFError) as error:
        print("Error:", error)
        return 1


if __name__ == "__main__":
    sys.exit(main())
