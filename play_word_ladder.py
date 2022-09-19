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

This module contains a basic text UI to allow you to play your
WordLadderPuzzle once you have completed the necessary parts of the assignment.
"""

from __future__ import annotations
from random import shuffle
from typing import Optional, Set
from solver import BfsSolver
from word_ladder_puzzle import WordLadderPuzzle, load_words


def make_word_ladder(difficulty: str = 'easy',
                     target_word: str = 'cost',
                     word_set: Optional[Set[str]] = None) -> \
        Optional[WordLadderPuzzle]:
    """
    Return a random WordLadderPlusPuzzle with the specified <difficulty> or None
    if there is no such puzzle.

    <difficulty> is one of 'easy' (default), 'medium', 'hard'.

    The other parameters are:

    <target_word> (default 'cost') - the word to use as the to_word

    <word_set> (default None) - the words to use in the WordLadderPuzzle
        (if None, uses load_words to use words from a file)

    The from_word is drawn randomly from word_set. Different from_words
    should be tried until either they have all been tried or a puzzle with
    the correct difficulty was found.

    Note: this is a rather inefficient way to do this
    (once you finish the assignment, you can try writing a
     smarter puzzle maker!)

    """
    if word_set is None:
        word_set = load_words()
    my_words = list(word_set)
    shuffle(my_words)  # try random from_words to make a puzzle
    for from_word in my_words:
        if len(from_word) == len(target_word):
            puz = WordLadderPuzzle(from_word, target_word, word_set)
            if puz.get_difficulty() == difficulty:
                return puz
    return None


def play_word_ladder(puz: WordLadderPuzzle) -> None:
    """
    Simple text UI to play a given word ladder plus puzzle
    """
    print("Controls:\n"
          "q to quit\n"
          "HINT for hint\n"
          "Good luck!\n")
    while not puz.is_solved():
        next_word = input(f"{puz}\ntype your next word: ")
        if next_word == "q":
            return
        elif next_word == "HINT":
            puz = BfsSolver().solve(puz)[1]
        else:
            next_puzzle = WordLadderPuzzle(next_word,
                                           puz.to_word,
                                           puz.word_set)
            if next_puzzle in puz.extensions():
                puz = next_puzzle
            else:
                print("invalid move, keep trying!\n"
                      "q to quit\n"
                      "HINT for hint\n")
    print("SOLVED!")


def play_game() -> None:
    """
    Simple text UI to play a word ladder plus puzzle.
    The user is prompted to choose the difficulty.
    """

    diff_choice = '1'
    difficulties = ['easy', 'medium', 'hard']
    target = 'cost'  # change this if you want a different puzzle to_word
    while diff_choice != 'q':
        diff_choice = input("select a difficulty:\n"
                            "1 = 'easy'\n"
                            "2 = 'medium'\n"
                            "3 = 'hard'\n"
                            "q = quit\nSelection:")
        try:
            diff_index = int(diff_choice)
            if not 1 <= diff_index <= 3:
                raise ValueError
            diff_index -= 1
            diff = difficulties[diff_index]
            puzzle = make_word_ladder(diff, target)
            if puzzle:
                play_word_ladder(puzzle)
            else:
                print("No puzzle could be created, make sure your"
                      "BfsSolver and the get_difficulty method"
                      "in class WordLadderPuzzle are both implemented"
                      "correctly.")
        except ValueError:
            pass


if __name__ == "__main__":
    play_game()
