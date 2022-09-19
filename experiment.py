"""
CSC148, Winter 2021
Assignment 2: Automatic Puzzle Solver
==============================
This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

Authors: Diane Horton, Jonathan Calver, Sophia Huynh,
         Maryam Majedi, and Jaisie Sin.

All of the files in this directory are:
Copyright (c) 2021 Diane Horton, Jonathan Calver, Sophia Huynh,
                   Maryam Majedi, and Jaisie Sin.

=== Module Description ===

This module contains experiment code that tries using the two solvers
on a couple of puzzles and prints a summary as a markdown table.

Feel free to add more samples here to explore how your solvers perform
under various conditions.

This file is NOT graded and is provided purely as a way for you to further
explore and develop your code if you wish to.

Things you might explore:

- implementing another puzzle type of your choice
- solving puzzles with different properties
- exploring how implementing fail_fast changes the time taken to solve puzzles
- implementing your own custom solver to try to get better performance
"""
from timeit import timeit
from solver import BfsSolver, DfsSolver
from sudoku_puzzle import SudokuPuzzle
from word_ladder_puzzle import WordLadderPuzzle

if __name__ == '__main__':

    puzzles = [SudokuPuzzle(4,
                            [["1", " ", " ", "2"],
                             [" ", " ", " ", "1"],
                             [" ", " ", " ", " "],
                             [" ", " ", "2", " "]],
                            {"1", "2", "3", "4"}),
               SudokuPuzzle(9,
                            [[" ", " ", " ", "7", " ", "8", " ", "1", " "],
                             [" ", " ", "7", " ", "9", " ", " ", " ", "6"],
                             ["9", " ", "3", "1", " ", " ", " ", " ", " "],
                             ["3", "5", " ", "8", " ", " ", "6", " ", "1"],
                             [" ", " ", " ", " ", " ", " ", " ", " ", " "],
                             ["1", " ", "6", " ", " ", "9", " ", "4", "8"],
                             [" ", " ", " ", " ", " ", "1", "2", " ", "7"],
                             ["8", " ", " ", " ", "7", " ", "4", " ", " "],
                             [" ", "6", " ", "3", " ", "2", " ", " ", " "]],
                            {"1", "2", "3", "4", "5", "6", "7", "8", "9"}),
               WordLadderPuzzle("same", "cost")
               ]
    headers = ["Puzzle Type", "Solver", "len(sol)", "time"]
    print("|".join(headers))
    print("|".join(["-" * len(header) for header in headers]))

    for puzzle in puzzles:
        for solver in [DfsSolver, BfsSolver]:
            puzzle_solver = solver()
            sol = puzzle_solver.solve(puzzle)
            n_samples = 1
            duration = timeit('puzzle_solver.solve(puzzle)',
                              globals=globals(),
                              number=n_samples) / n_samples

            print(f"{type(puzzle).__name__[:-6]:>11}|{solver.__name__[:-6]:>6}|"
                  f"{len(sol) if sol else -1:>8}|{duration:2.5f}")
