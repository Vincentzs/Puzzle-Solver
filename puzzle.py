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

This module contains the abstract Puzzle class.

DO NOT MODIFY ANYTHING IN THIS MODULE.
"""

from __future__ import annotations
from typing import List


class Puzzle:
    """"
    A full-information puzzle, which may be solved, unsolved,
    or even unsolvable. This is an abstract class.
    """

    def fail_fast(self) -> bool:
        """
        Return True if this Puzzle can never be solved.
        Note: fail_fast may return False in some situations where
        it can't EASILY be determined that the puzzle has no solution.

        Override this in a subclass where you can EASILY determine that
        this Puzzle can't be solved.
        """
        return False

    def is_solved(self) -> bool:
        """
        Return True iff this Puzzle is in a solved state.

        This is an abstract method that must be implemented
        in a subclass.
        """
        raise NotImplementedError

    def extensions(self) -> List[Puzzle]:
        """
        Return a list of legal extensions of this Puzzle.

        If this Puzzle has no legal extensions, then an empty list
        should be returned.

        This is an abstract method that must be implemented
        in a subclass.
        """
        raise NotImplementedError
