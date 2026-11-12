""""Read our board and follow its lasers.""""


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


if __name__ == "__main__":
    filename = input("Enter the .bff filename: ").strip()

    try:
        board = read_bff(filename)
        reached = simulate_lasers(board)

        hits = 0

        for target in board.targets:
            if target in reached:
                hits += 1

        print("Movable blocks:", board.blocks)
        print("Targets reached:", hits)
        print("Total targets:", len(board.targets))

        if hits == len(board.targets):
            print("All targets were reached.")
        else:
            print("Some targets were not reached.")

    except (OSError, ValueError) as error:
        print("Error:", error)