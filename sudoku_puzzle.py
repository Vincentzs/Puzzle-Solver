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

This module contains the sudoku puzzle class.

Note: Some of the provided code makes use of list comprehensions
      and can be a bit hard to understand if you aren't familiar with
      them. You do NOT need to understand HOW the provided code works,
      but you need to understand WHAT services it is providing, so that you
      can make use of the provided private methods to help you with the task of
      implementing fail_fast.
"""

from __future__ import annotations
from typing import List, Set
from puzzle import Puzzle
from solver import BfsSolver

EMPTY_CELL = ' '


# n = 0


class SudokuPuzzle(Puzzle):
    """
    A Sudoku puzzle.

    === Private Attributes ===
    _n: the number of rows/columns in this puzzle's grid
    _grid: the grid representing this puzzle; each sublist
          represents one row of the grid
    _symbol_set: the set of all symbols that each row/column/subsquare must have
      exactly one of, for this puzzle to be solved


    === Representation Invariants ===
    _n is a positive, square integer >= 4 (e.g. 4, 9, 16)
    """
    _n: int
    _grid: List[List[str]]
    _symbol_set: Set[str]

    def __init__(self, n: int, grid: List[List[str]],
                 symbol_set: Set[str]) -> None:
        """
        Create a new n x n SudokuPuzzle with symbols
        from <symbol_set> and the specified <grid>.

        Note:
        - Grid symbols are represented as letters or numerals
          and must be single characters.
        - In <grid>, an empty square is represented by the constant
          EMPTY_CELL
        - a copy of grid is NOT made

        Preconditions:
        - n is a positive, square integer, n >= 4 (e.g. 4, 9, 16)
        - there are n symbols in the given symbol_set
        - there are n lists in grid, and each list has n symbols, each of which
          is either an EMPTY_CELL or in the symbol_set.
        """

        self._n, self._grid, self._symbol_set = n, grid, symbol_set

    def __eq__(self, other: SudokuPuzzle) -> bool:
        """
        Return True if this SudokuPuzzle is equivalent to <other>, False
        otherwise.

        Two SudokuPuzzles are equivalent if they have equal grids
        and equal symbol sets.

        >>> r1 = ["A", "B", "C", "D"]
        >>> r2 = ["D", "C", "B", "A"]
        >>> r3 = [" ", "D", " ", " "]
        >>> r4 = [" ", " ", " ", " "]
        >>> s1 = SudokuPuzzle(4, [r1, r2, r3, r4], {"A", "B", "C", "D"})
        >>> r1_2 = ["A", "B", "C", "D"]
        >>> r2_2 = ["D", "C", "B", "A"]
        >>> r3_2 = [" ", "D", " ", " "]
        >>> r4_2 = [" ", " ", " ", " "]
        >>> s2 = SudokuPuzzle(4, [r1_2, r2_2, r3_2, r4_2], {"A", "B", "C", "D"})
        >>> s1 == s2
        True
        >>> r1_3 = ["A", "B", "C", "D"]
        >>> r2_3 = ["D", "C", "B", "A"]
        >>> r3_3 = [" ", "D", " ", " "]
        >>> r4_3 = [" ", "A", " ", " "]
        >>> s3 = SudokuPuzzle(4, [r1_3, r2_3, r3_3, r4_3], {"A", "B", "C", "D"})
        >>> s1 == s3
        False
        """
        return (self._grid == other._grid
                and self._symbol_set == other._symbol_set)

    def __str__(self) -> str:
        """
        Return a human-readable string representation of this SudokuPuzzle.

        >>> r1 = ["A", "B", "C", "D"]
        >>> r2 = ["D", "C", "B", "A"]
        >>> r3 = [" ", "D", " ", " "]
        >>> r4 = [" ", " ", " ", " "]
        >>> s = SudokuPuzzle(4, [r1, r2, r3, r4], {"A", "B", "C", "D"})
        >>> print(s)
        -------
        |AB|CD|
        |DC|BA|
        -------
        | D|  |
        |  |  |
        -------
        >>> s = SudokuPuzzle(9, \
                      [[" ", " ", " ", "9", " ", "2", " ", " ", " "], \
                       [" ", "9", "1", " ", " ", " ", "6", "3", " "], \
                       [" ", "3", " ", " ", "7", " ", " ", "8", " "], \
                       ["3", " ", " ", " ", " ", " ", " ", " ", "8"], \
                       [" ", " ", "9", " ", " ", " ", "2", " ", " "], \
                       ["5", " ", " ", " ", " ", " ", " ", " ", "7"], \
                       [" ", "7", " ", " ", "8", " ", " ", "4", " "], \
                       [" ", "4", "5", " ", " ", " ", "8", "1", " "], \
                       [" ", " ", " ", "3", " ", "6", " ", " ", " "]], \
                      {"1", "2", "3", "4", "5", "6", "7", "8", "9"})
        >>> print(s)
        -------------
        |   |9 2|   |
        | 91|   |63 |
        | 3 | 7 | 8 |
        -------------
        |3  |   |  8|
        |  9|   |2  |
        |5  |   |  7|
        -------------
        | 7 | 8 | 4 |
        | 45|   |81 |
        |   |3 6|   |
        -------------
        """
        rslt = ''
        sqn = round(self._n ** (1 / 2))

        div = "-" * (self._n + sqn + 1) + "\n"

        for i in range(self._n):
            if i % sqn == 0:
                rslt += div
            row = '|'
            for j in range(sqn):
                row = (row
                       + "".join(self._grid[i][j * sqn: (j + 1) * sqn]) + '|')
            rslt += row + '\n'
        rslt += div
        return rslt.rstrip()

    def is_solved(self) -> bool:
        """
        Return True if this SudokuPuzzle is solved, False otherwise.

        >>> r1 = ["A", "B", "C", "D"]
        >>> r2 = ["C", "D", "A", "B"]
        >>> r3 = ["B", "A", "D", "C"]
        >>> r4 = ["D", "C", "B", "A"]
        >>> grid = [r1, r2, r3, r4]
        >>> s = SudokuPuzzle(4, grid, {"A", "B", "C", "D"})
        >>> s.is_solved()
        True
        >>> r1 = ["A", "B", "C", "D"]
        >>> r2 = ["C", "D", "A", "B"]
        >>> r3 = ["B", "D", "A", "C"]  # "D" and "A" in this row are not valid.
        >>> r4 = ["D", "C", "B", "A"]
        >>> grid = [r1, r2, r3, r4]
        >>> s = SudokuPuzzle(4, grid, {"A", "B", "C", "D"})
        >>> s.is_solved()
        False
        """
        # check if there are any EMPTY_CELLs left
        if any(EMPTY_CELL in row for row in self._grid):
            return False
        # check that all rows and columns have correct symbols
        for i in range(self._n):
            for j in range(self._n):
                # row
                if self._row_set(i) != self._symbol_set:
                    return False
                if self._column_set(j) != self._symbol_set:
                    return False
        # check that all subsquares have correct symbols
        sqn = round(self._n ** 0.5)
        for i in range(0, self._n, sqn):
            for j in range(0, self._n, sqn):
                if self._subsquare_set(i, j) != self._symbol_set:
                    return False
        return True

    def extensions(self) -> List[SudokuPuzzle]:
        """
        Return list of extensions of SudokuPuzzle self.

        Note: For sudoku puzzles, we define the extensions to be puzzles
              where the first empty square (starting from the top left corner
              reading left to right and then top to bottom) is filled in
              with a symbol not already occuring in that row, column, or
              subsquare.

        >>> r1 = ["A", "B", "C", "D"]
        >>> r2 = ["C", "D", "A", "B"]
        >>> r3 = ["B", "A", "D", "C"]
        >>> r4 = ["D", "C", "B", " "]
        >>> grid = [r1, r2, r3, r4]
        >>> s = SudokuPuzzle(4, grid, {"A", "B", "C", "D"})
        >>> L1 = list(s.extensions())
        >>> grid[-1][-1] = "A"
        >>> L2 = [SudokuPuzzle(4, grid, {"A", "B", "C", "D"})]
        >>> len(L1) == len(L2)
        True
        >>> all([s in L2 for s in L1])
        True
        >>> all([s in L1 for s in L2])
        True
        """
        # temporary variables to give convenient names to each attribute
        symbols, symbol_set, n = self._grid, self._symbol_set, self._n
        if not any(EMPTY_CELL in row for row in symbols):
            return []
        # get position of first empty position
        r = 0  # row with first empty position
        while EMPTY_CELL not in symbols[r]:
            r += 1
        c = symbols[r].index(EMPTY_CELL)  # column with first empty position

        # allowed symbols at position (r, c)
        # A | B == A.union(B)
        allowed_symbols = sorted(self._symbol_set
                                 - (self._row_set(r)
                                    | self._column_set(c)
                                    | self._subsquare_set(r, c)))
        # print(allowed_symbols)

        # list of SudokuPuzzles with each legal digit at position r, c
        return_lst = []
        for symbol in allowed_symbols:
            # NOTE: type(self)(...) means create a new SudokuPuzzle,
            # we do this here so that if we were to create a subclass of
            # SudokuPuzzle later, then this will work as intended
            new_puzzle = type(self)(n, symbols[:r]
                                    + [symbols[r][:c]
                                       + [symbol]
                                       + symbols[r][c + 1:]]
                                    + symbols[r + 1:], symbol_set)
            return_lst.append(new_puzzle)
        return return_lst

    # TO DO (Task 1): override fail_fast
    # If there is an open position with no symbols available
    # (i.e. all symbols are already used in the same row, column, or subsquare),
    # then the sudoku puzzle is not solvable.
    #
    # Hint: You may find the provided private methods below helpful.
    #       The helpers return sets - see the provided code for extensions
    #       above for an example of how they can be used.
    #
    # Note: You can take the union of two sets, set_a and set_b as either
    #       set_a | set_b or set_a.union(set_b).
    #       Example:
    #            {'1', '2', '3'} | {'2', '4', '5'} == {'1', '2', '3', '4', '5'}
    def fail_fast(self) -> bool:
        """
        Return True if some unfilled position has no allowable symbols
        remaining to choose from, and hence this SudokuPuzzle can never
        be completed, and False otherwise.

        >>> s = SudokuPuzzle(4, \
        [["A", "B", "C", "D"], \
        ["C", "D", " ", " "], \
        [" ", " ", " ", " "], \
        [" ", " ", " ", " "]], {"A", "B", "C", "D"})
        >>> s.fail_fast()
        False
        >>> s = SudokuPuzzle(4, \
        [["B", "D", "A", "C"], \
        ["C", "A", "B", "D"], \
        ["A", "B", " ", " "], \
        [" ", " ", " ", " "]], {"A", "B", "C", "D"})
        >>> s.fail_fast()
        True
        """
        symbols = self._grid
        allowed_symbols = self._fail_fast_helper()
        if not any(EMPTY_CELL in row for row in symbols):
            return False
        for symbol in allowed_symbols:
            if len(symbol) == 0:
                return True
        return False

    def _fail_fast_helper(self) -> List[Set[str]]:
        """ fail_fast_helper returns a list of sets of allowed_symbols
        """
        symbols, n = self._grid, self._n
        allowed_symbols = []
        for r in range(n):
            for c in range(n):
                if symbols[r][c] == EMPTY_CELL:
                    allowed_symbols.append((self._symbol_set
                                            - (self._row_set(r)
                                               | self._column_set(c)
                                               | self._subsquare_set(r, c))))
        return allowed_symbols

    # some private helper methods
    # Note: these return sets of symbols you may find useful
    def _row_set(self, r: int) -> Set[str]:
        # Return set of symbols in row r of SudokuPuzzle self's grid.

        # set of elements from grid[r]
        return set(self._grid[r])

    def _column_set(self, c: int) -> Set[str]:
        # Return set of symbols in column c of SudokuPuzzle self's grid.

        # set of elements from grid[0][c], grid[1][c],
        # ... grid[len(grid)-1][c]
        return set(row[c] for row in self._grid)

    def _subsquare_set(self, r: int, c: int) -> Set[str]:
        # Return set of symbols in subsquare of SudokuPuzzle self's grid
        # where position r, c occurs.

        # length of subsquares
        ss = round(self._n ** (1 / 2))
        # upper-left position of the subsquare containing r, c
        ul_row = (r // ss) * ss
        ul_col = (c // ss) * ss

        subsquare_symbols = []
        for i in range(ss):
            for j in range(ss):
                subsquare_symbols.append(self._grid[ul_row + i][ul_col + j])
        return set(subsquare_symbols)

    # TO DO (Task 2): implement has_unique_solution
    # Implement this method according to its docstring
    # You may import any modules that you need when implementing this method.
    def has_unique_solution(self) -> bool:
        """
        Return True if the this Sudoku puzzle has exactly one unique solution,
        and False otherwise.

        Two "solutions" are considered to be equal if the final puzzle
        state is the same.

        Hint: You should find the optional parameter, seen, for the Solver
        class' solve method very useful here.
        """
        bfs = BfsSolver()
        result = bfs.solve(self)
        if not result:
            return False
        else:
            seen = {str(result[-1])}
            return bfs.solve(self, seen) == []


if __name__ == "__main__":
    # any code you want to use for testing your code above

    # from doctest import testmod
    # testmod()

    # s1 = SudokuPuzzle(9,
    #                  [["2", "3", "7", "8", " ", "1", " ", " ", " "],
    #                   [" ", " ", " ", " ", " ", " ", " ", "4", "3"],
    #                   ["5", " ", " ", " ", " ", "6", " ", " ", " "],
    #                   [" ", " ", "5", " ", "7", " ", "8", " ", " "],
    #                   [" ", " ", " ", " ", " ", " ", "1", " ", " "],
    #                   [" ", "2", " ", " ", "3", " ", " ", " ", " "],
    #                   ["6", " ", " ", " ", " ", " ", " ", "7", "5"],
    #                   [" ", " ", "3", "4", " ", " ", " ", " ", " "],
    #                   [" ", " ", " ", "2", " ", " ", "6", " ", " "]],
    #                  {"1", "2", "3", "4", "5", "6", "7", "8", "9"})
    # print(s1.fail_fast())
    # # print(f'{n} steps.')
    #
    # s2 = SudokuPuzzle(9,
    #                   [[" ", " ", " ", "9", " ", "2", " ", " ", " "],
    #                    [" ", "9", "1", " ", " ", " ", "6", "3", " "],
    #                    [" ", "3", " ", " ", "7", " ", " ", "8", " "],
    #                    ["3", " ", " ", " ", " ", " ", " ", " ", "8"],
    #                    [" ", " ", "9", " ", " ", " ", "2", " ", " "],
    #                    ["5", " ", " ", " ", " ", " ", " ", " ", "7"],
    #                    [" ", "7", " ", " ", "8", " ", " ", "4", " "],
    #                    [" ", "4", "5", " ", " ", " ", "8", "1", " "],
    #                    [" ", " ", " ", "3", " ", "6", " ", " ", " "]],
    #                   {"1", "2", "3", "4", "5", "6", "7", "8", "9"})
    # print(s2.fail_fast())

    # r1 = ["A", " ", "C", " "]
    # r2 = [" ", "B", " ", " "]
    # r3 = [" ", "C", " ", " "]
    # r4 = [" ", " ", " ", "D"]
    # grid = [r1, r2, r3, r4]
    # s = SudokuPuzzle(4, grid, {"A", "B", "C", "D"})
    # print(s.fail_fast())

    import python_ta

    python_ta.check_all(config={'pyta-reporter': 'ColorReporter',
                                'allowed-io': [],
                                'allowed-import-modules': ['doctest',
                                                           'python_ta',
                                                           'typing',
                                                           'puzzle',
                                                           '__future__',
                                                           'solver'],
                                'disable': ['E1136'],
                                'max-attributes': 15}
                        )
