# Lazors Project

## Group members
- Anar Nuruzada: block-placement solver, solution checking, and solution output.
- Arun Tailor: BFF file reading, block class, and laser simulation.

## What the program does
The program reads a Lazors puzzle from a `.bff` file and tries different placements of the available blocks. It follows the laser paths and saves the first arrangement that reaches every target. It supports reflective blocks (A), opaque blocks (B), refractive blocks (C), and fixed blocks.

## Requirements
Python 3. No additional Python packages are required.

## How to run
From the project folder, run:

```sh
python3 LazorGroupProjectAnarArun.py example.bff
```

Replace `example.bff` with the puzzle filename you want to solve.

## Output
A successful run creates a file such as `example_solution.bff` containing the solved board, lasers, and targets.

In the grid:
- A = reflective block
- B = opaque block
- C = refractive block
- o = empty space where blocks are allowed
- x = space where blocks are not allowed

If no arrangement works, the program reports that no solution was found. Existing output files are not overwritten; use a different output filename for another run:

```sh
python3 LazorGroupProjectAnarArun.py example.bff another_solution.bff
```

## Example puzzles
Four small puzzles were created for manual testing:
- `example.bff`: reflection.
- `example2.bff`: refraction reaching two targets.
- `example3.bff`: placement of an opaque block.
- `example4.bff`: fixed and movable reflective blocks.

All four were run successfully, and their output grids were checked against the expected arrangements. 
