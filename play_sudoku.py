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

This module contains a basic GUI to allow you to play randomly generated
instances of your SudokuPuzzle once you have completed the necessary parts
of the assignment. When run, instructions on how to use it are displayed
in the console.

Feel free to modify this module.
"""
from __future__ import annotations
from typing import List, Tuple

from random import randint, shuffle
# imports for the GUI
import pygame
import pygame_gui
from pygame.event import Event
from pygame_gui.core.interfaces import IUIManagerInterface
from pygame_gui.elements import UIButton, UILabel
# imports from our code
from puzzle import Puzzle
from solver import DfsSolver
from sudoku_puzzle import SudokuPuzzle, EMPTY_CELL

# You can configure the settings here
N = 4  # puzzle size - suggested is either 4 or 9 (untested on 16)

# Pick how many numbers you want in the grid
# Don't pick this too small or it might be slow to generate a puzzle for you!
# NUM_STARTING = N ** 2 // 2  # this is a fairly easy puzzle
NUM_STARTING = N ** 2 // 3  # slightly harder, but still easy
# NUM_STARTING = N ** 2 // 4  # slightly harder, may generate somewhat slowly.


# Some constants defining the size of the GUI, may need to adjust
# depending on the size of screen.
WIDTH = 800
HEIGHT = 800
UI_WIDTH = WIDTH
UI_HEIGHT = HEIGHT
UI_ITEM_HEIGHT = HEIGHT // (N + 2)  # +2 to account for buttons at the bottom.
UI_ITEM_WIDTH = WIDTH // N


# An example of how we can extend our SudokuPuzzle class to give it more
# features.
class RandomizedSudokuPuzzle(SudokuPuzzle):
    """
    A sudoku puzzle where we randomize the extensions - allowing us
    to randomly generate puzzles.
    """

    # This is why we were using type(self)(...) in the SudokuPuzzle
    # extensions method - otherwise this wouldn't do what we intended.
    def extensions(self) -> List[RandomizedSudokuPuzzle]:
        """
        Return a list of extensions of this sudoku puzzle.
        The order of the extensions is randomized.
        """
        exts = SudokuPuzzle.extensions(self)
        shuffle(exts)
        return exts

    # some other methods we'll use to help us in our GUI
    def copy_grid(self) -> List[List[str]]:
        """
        Return a copy of this sudoku's grid
        """
        return [[self._grid[i][j] for j in range(self._n)]
                for i in range(self._n)]

    def get_possible(self, r: int, c: int) -> List[str]:
        """
        Get the list of possible symbols that can go in position <r>, <c>.
        """
        allowed_symbols = (self._symbol_set
                           - (self._row_set(r)
                              | self._column_set(c)
                              | self._subsquare_set(r, c)))
        return sorted(list(allowed_symbols))


# This is the part that makes use of our
# DfsSolver.solve method and SudokuPuzzle.has_unique_solution method
# Note: This approach is rather inefficient, but demonstrates a
#       straightforward, intuitive way of generating a valid sudoku puzzle.
def make_sudoku(n: int = N,
                num_starting: int =
                NUM_STARTING) -> Tuple[RandomizedSudokuPuzzle,
                                       Puzzle]:
    """
    Generate a valid sudoku of grid size <n> x <n>.

    This function attempts to leave <num_starting> squares with numbers in them.
    """
    # generate a random filled sudoku grid... using our solver!
    grid = [[' ' for i in range(n)] for j in range(n)]
    symbols = {str(i) for i in range(1, n + 1)}
    s = RandomizedSudokuPuzzle(n, grid, symbols)

    # Note: Since extensions always works from top left to bottom right,
    # only the final solution is really of any use to us - if extensions
    # instead randomly chose a square to fill in, then we could consider
    # looking back through the solution path for a potential puzzle.
    puzzle_solution = DfsSolver().solve(s)[-1]

    # We'll randomly remove some values from the solved puzzle,
    # ensuring not to violate uniqueness of the solution.

    num_to_remove = n ** 2 - num_starting

    # can fiddle with somewhat to try to decrease the time to generate puzzles
    batch_size = max(1, num_to_remove // 10)
    give_up_limit = num_to_remove // batch_size + batch_size

    grid = puzzle_solution.copy_grid()
    solution_grid = puzzle_solution.copy_grid()
    puzzle = puzzle_solution
    while num_to_remove > 0 and give_up_limit > 0:

        num = max(1, min(num_to_remove, batch_size))
        # get num random (r, c)'s to try to remove
        pairs = []
        while len(pairs) < num:
            r = randint(0, n - 1)
            c = randint(0, n - 1)
            if (r, c) not in pairs and grid[r][c] != EMPTY_CELL:
                pairs.append((r, c))
                grid[r][c] = EMPTY_CELL

        # now ensure the puzzle still has a unique solution
        puzzle = RandomizedSudokuPuzzle(n, grid, symbols)

        # if the puzzle is still unique, we can remove the numbers.
        if puzzle.has_unique_solution():
            num_to_remove -= num
        else:  # removing the numbers broke the uniqueness, so put them back.
            for r, c in pairs:
                grid[r][c] = solution_grid[r][c]
            batch_size -= 1
        # just to ensure we always return a puzzle eventually!
        give_up_limit -= 1

    return puzzle, puzzle_solution


class SudokuPuzzleGUI:
    """
    Simple GUI for a Sudoku puzzle

    === Private Attributes ===
    _puzzle: the sudoku puzzle
    _manager: manager for the pygame gui
    _window_surface: pygame surface for displaying the game
    _is_running: whether or not the game is running
    _buttons: list of labels containing the grid values
    _hint_button: button for getting a checking correct values
    _new_button: button for getting a new puzzle
    _hint_toggle: button to toggle tool tip hints on and off
    _solved_label: label to display when puzzle is solved
    _hints_on: flag indicating if hints are enabled
    _solution_grid: grid of the solved puzzle
    _grid: grid of the current puzzle state
    """

    _puzzle: RandomizedSudokuPuzzle
    _manager: IUIManagerInterface
    _window_surface: pygame.Surface
    _is_running: bool

    _buttons: List[List[UIButton]]
    _hint_button: UIButton
    _new_button: UIButton
    _hint_toggle: UIButton
    _solved_label: UILabel

    _hints_on: bool

    _solution_grid: List[List[str]]
    _grid: List[List[str]]

    def __init__(self) -> None:
        """

        """
        pygame.init()
        self._window_surface = pygame.display.set_mode((WIDTH, HEIGHT))
        self._manager = pygame_gui.UIManager((UI_WIDTH, UI_HEIGHT))

        self._manager.get_theme().load_theme('themes/button.json')
        self._manager.get_theme().load_theme('themes/label.json')

        self._setup_puzzle()

        self._setup_ui()  # note, this helper creates some of the attributes

        self._is_running = False

    def _check_if_solved(self) -> None:
        """
        Check if the user action caused the puzzle to be solved and
        update the GUI accordingly.
        """
        if self._puzzle.is_solved():
            self._solved_label.visible = 1
        else:
            self._solved_label.visible = 0

    def _get_hint(self) -> None:
        """
        Check which of the filled in squares are correct.

        If a square is correct, disable the button.
        """
        for i in range(N):
            for j in range(N):
                if self._grid[i][j] == self._solution_grid[i][j]:
                    self._buttons[i][j].disable()

    def _update_all_tool_tips(self) -> None:
        """
        Update all tool tips on the grid.
        """
        # reset the tool tips appropriately
        for i in range(N):
            for j in range(N):
                if not self._hints_on:
                    self._buttons[i][j].tool_tip_text = None
                elif self._buttons[i][j].is_enabled:
                    self._update_tool_tip(i, j)

    def _update_tool_tip(self, r: int, c: int) -> None:
        """
        Update the tool tip to contain the set of possible numbers
        that can go in square <r>, <c> in the sudoku puzzle.
        """
        tmp, self._grid[r][c] = self._grid[r][c], EMPTY_CELL
        ops = self._puzzle.get_possible(r, c)
        self._grid[r][c] = tmp
        self._buttons[r][c].tool_tip_text = str(ops)

    def _update_tool_tips(self, r: int, c: int) -> None:
        """
        update the tool tip text for each button in this
        row, column, and subsquare...
        """
        for ci in range(N):
            if ci != c:
                self._update_tool_tip(r, ci)
        for ri in range(N):
            if ri != r:
                self._update_tool_tip(ri, c)

        sqn = round(N ** 0.5)
        # do subsquare too
        ro = r // sqn * sqn
        co = c // sqn * sqn
        for ri in range(sqn):
            for ci in range(sqn):
                self._update_tool_tip(ro + ri, co + ci)

    def _process_grid_press(self, event: Event) -> None:
        """
        Update the grid and puzzle based on the button pressed
        """
        button = event.ui_element
        c = N
        r = 0
        while c == N and r < N:
            if button in self._buttons[r]:
                c = self._buttons[r].index(button)
            else:
                r += 1
        if c != N and self._buttons[r][c].is_enabled:
            cur = button.text
            self._grid[r][c] = EMPTY_CELL
            ops = self._puzzle.get_possible(r, c)
            self._grid[r][c] = cur

            # go to the next choice
            if ops and cur not in ops:
                cur = ops[0]
            elif ops:
                d = ops.index(cur) + 1
                if d >= len(ops):
                    cur = EMPTY_CELL
                else:
                    cur = ops[d]
            else:
                cur = EMPTY_CELL
            self._grid[r][c] = cur
            button.set_text(cur)
            # if hints are on, update the tool tips accordingly
            if self._hints_on:
                self._update_tool_tips(r, c)

    def _toggle_hints(self) -> None:
        """
        Toggle the tool tip hints.
        """
        if self._hints_on:
            self._hint_toggle.set_text("HINTS OFF")
        else:
            self._hint_toggle.set_text("HINTS ON")
        self._hints_on = not self._hints_on
        self._update_all_tool_tips()

    def _process_event(self, event: Event) -> None:
        """
        Processes a pygame event - which will be one of:
            - the user quit
            - new button pressed
            - hint ("check") button pressed
            - hint toggle button pressed
            - grid square button pressed
        """
        if event.type == pygame.QUIT:
            self._is_running = False

        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self._new_button:
                    # create a new puzzle
                    self._setup_puzzle()
                    # redo the GUI...
                    self._manager.clear_and_reset()
                    self._setup_ui()

                elif event.ui_element == self._hint_button:
                    self._get_hint()
                elif event.ui_element == self._hint_toggle:
                    self._toggle_hints()
                else:  # one of the grid squares
                    self._process_grid_press(event)

            self._check_if_solved()

    def _draw_grid(self) -> None:
        """
        Draw the lines dividing the subsquares.
        """

        for i in range(1, int(N ** 0.5)):

            pygame.draw.line(self._window_surface, (25, 25, 25),

                             (0, UI_ITEM_HEIGHT * i * N ** 0.5),
                             (UI_ITEM_WIDTH * N, UI_ITEM_HEIGHT * i * N ** 0.5),
                             4)

            pygame.draw.line(self._window_surface, (25, 25, 25),

                             (UI_ITEM_WIDTH * i * N ** 0.5, 0),
                             (UI_ITEM_WIDTH * i * N ** 0.5, UI_ITEM_HEIGHT * N),
                             4)

    def play_game(self) -> None:
        """
        Main loop for playing a sudoku puzzle in the GUI.
        """
        pygame.display.set_caption('CSC148 Sudoku 2021')
        clock = pygame.time.Clock()
        self._is_running = True

        while self._is_running:
            time_delta = clock.tick(10)
            for event in pygame.event.get():
                self._process_event(event)
                self._manager.process_events(event)
                # update the game's display
                self._manager.update(time_delta)
                background = (255, 255, 255)
                self._window_surface.fill(background)

                self._draw_grid()

                self._manager.draw_ui(self._window_surface)
                pygame.display.update()

    def _setup_puzzle(self) -> None:
        """
        Generate a random expression tree puzzle and create the image for it.
        This helper is called inside the __init__ and creates several of the
        private instance attributes. It is called again any time the puzzle
        to be solved is changed (the new button is pressed).
        """
        raw_puzzle, solution = make_sudoku()
        self._grid = raw_puzzle.copy_grid()
        self._solution_grid = solution.copy_grid()
        # Note: we'll take advantage of aliasing here. Since our
        # SudokuPuzzle class doesn't make its own copy of the grid we pass in,
        # we can directly update self._grid to change the state of the puzzle!
        self._puzzle = RandomizedSudokuPuzzle(N, self._grid,
                                              {str(i) for i in range(1, N + 1)})

    def _setup_ui(self) -> None:
        """
        Set up the UI components for the game.
        This helper is called inside the __init__ and creates several of the
        private instance attributes. It is called again any time the puzzle
        to be solved is changed.
        """
        self._buttons = []

        for i in range(N):
            row = []
            for j in range(N):
                rect = pygame.Rect(
                    (UI_ITEM_WIDTH * j + 2, UI_ITEM_HEIGHT * i + 2),
                    (UI_ITEM_WIDTH - 2, UI_ITEM_HEIGHT - 2))

                tip = str(self._puzzle.get_possible(i, j))
                if self._grid[i][j] == self._solution_grid[i][j]:
                    tip = None

                label = UIButton(relative_rect=rect,
                                 text=self._grid[i][j],
                                 tool_tip_text=tip,
                                 manager=self._manager)
                if self._grid[i][j] != EMPTY_CELL:
                    label.disable()

                row.append(label)
            self._buttons.append(row)

        rect = pygame.Rect((0, UI_ITEM_HEIGHT * N),
                           ((UI_ITEM_WIDTH * N) // 2, UI_ITEM_HEIGHT))
        self._hint_button = UIButton(relative_rect=rect,
                                     text='CHECK',
                                     manager=self._manager)

        rect = pygame.Rect(((UI_ITEM_WIDTH * N) // 2, UI_ITEM_HEIGHT * N),
                           ((UI_ITEM_WIDTH * N) // 2, UI_ITEM_HEIGHT))
        self._hint_toggle = UIButton(relative_rect=rect,
                                     text='HINTS ON',
                                     manager=self._manager)
        self._hints_on = True

        rect = pygame.Rect((0, UI_ITEM_HEIGHT * (N + 1)),
                           (UI_ITEM_WIDTH * N, UI_ITEM_HEIGHT))
        self._new_button = UIButton(relative_rect=rect,
                                    text='NEW',
                                    manager=self._manager)

        # solved label
        rect = pygame.Rect(
            (UI_ITEM_WIDTH * (N / 2) - UI_ITEM_WIDTH,
             UI_ITEM_HEIGHT * (N / 2) - UI_ITEM_HEIGHT / 2),
            (UI_ITEM_WIDTH * 2, UI_ITEM_HEIGHT))
        self._solved_label = UILabel(rect, "SOLVED!", manager=self._manager,
                                     visible=0)


def show_instructions() -> None:
    """
    Print instructions for how to use the GUI to the console.
    """
    # ASCII art (Ogre font) generated using:
    # https://www.colorschemer.com/ascii-art-generator/
    print(r"""
================================================================================
       ___  __    ___  _ _  _    ___    __           _       _          
      / __\/ _\  / __\/ | || |  ( _ )  / _\_   _  __| | ___ | | ___   _ 
     / /   \ \  / /   | | || |_ / _ \  \ \| | | |/ _` |/ _ \| |/ / | | |
    / /___ _\ \/ /___ | |__   _| (_) | _\ \ |_| | (_| | (_) |   <| |_| |
    \____/ \__/\____/ |_|  |_|  \___/  \__/\__,_|\__,_|\___/|_|\_\\__,_|                                                                    
================================================================================
HOW TO CHANGE PUZZLE SIZE AND HOW MANY STARTING NUMBERS ARE IN THE GRID:

In play_sudoku.py you can change the two values below and rerun the file.
    - N is the puzzle size - it should be either 4 or 9
    - NUM_STARTING is roughly how many numbers will be in the grid to start
        - you can see the make_sudoku function to see how the puzzle
          gets generated using the code you wrote for DfsSolver.solve and
          SudokuPuzzle.has_unique_solution!
================================================================================
HOW TO PLAY:
             
NEW - generate a new puzzle
CHECK - any VALUES you have entered that are CORRECT will become FIXED
HINTS ON/OFF - when ON, a tool tip menu shows what VALUES can go in a
               square when you hover over it.
CLICKING A SQUARE - changes the VALUE in the square - cycling through the
                    possible VALUES that could go in that square each time
                    you click on it.
================================================================================
""")


if __name__ == '__main__':
    show_instructions()

    gui = SudokuPuzzleGUI()
    gui.play_game()
