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

This module contains a basic GUI to allow you to play your
ExpressionTreePuzzle once you have completed the necessary parts
of the assignment.
"""
from __future__ import annotations
from typing import Dict, List, Tuple

from random import randint, choice, shuffle
# imports for the GUI
import pygame
import pygame
from pygame.event import Event
from pygame.core.interfaces import IUIManagerInterface
from pygame.elements import UIButton, UILabel, UIDropDownMenu
# imports from our code
from expression_tree import ExprTree, OPERATORS, visualize
from expression_tree_puzzle import ExpressionTreePuzzle
from solver import BfsSolver

# some constants defining how game is displayed
WIDTH = 1000
HEIGHT = 800
UI_WIDTH = 160
UI_HEIGHT = HEIGHT
UI_ITEM_HEIGHT = 40


def generate_random_expression_tree() -> Tuple[ExprTree,
                                               Dict[str, int]]:
    """
    Generate a random expression tree and its lookup dictionary.
    """

    # randomly pick how many variables to have
    var = {'a': randint(0, 2), 'b': randint(0, 2), 'c': randint(0, 2)}

    # ensure at least one variable
    if all([var[v] == 0 for v in var]):
        var['a'] = 1

    # start with a set of leaves
    subtrees = []
    for k in var:
        for _ in range(var[k]):
            subtrees.append(ExprTree(k, []))
    for _ in range(randint(1, 5)):
        subtrees.append(ExprTree(randint(1, 9), []))
    shuffle(subtrees)

    # iteratively form subtrees - starting form our initial set of leaves
    while len(subtrees) > 1:
        op = choice(OPERATORS)
        num_children = randint(2, min(3, len(subtrees)))
        nu_node = ExprTree(op, subtrees[-num_children:])
        for _ in range(num_children):
            subtrees.pop()
        subtrees.insert(randint(0, len(subtrees)), nu_node)

    # there is one tree left in subtrees - this is the root we will return,
    # but first, we will setup its lookup
    lookup = {}
    subtrees[0].populate_lookup(lookup)  # set_lookup recursively sets lookup
    return subtrees[0], lookup


class ExpressionTreePuzzleGUI:
    """
    Simple GUI for the ExpressionTreePuzzle

    === Private Attributes ===
    _tree: the expression tree
    _puzzle: the expression tree puzzle
    _expr_img: pygame surface for the image of the expression tree
    _manager: manager for the pygame gui
    _window_surface: pygame surface for displaying the game
    _is_running: whether or not the game is running
    _variable_map: list of dropdowns containing variable values
    _variable_name: list of labels containing variable names
    _target_label: label where target is displayed
    _result_label: label where the tree's evaluation is displayed
    _hint_button: button for getting a hint
    _new_button: button for getting a new puzzle
    """

    _tree: ExprTree
    _puzzle: ExpressionTreePuzzle
    _expr_img: pygame.Surface
    _manager: IUIManagerInterface
    _window_surface: pygame.Surface
    _is_running: bool

    _variable_map: List[UIDropDownMenu]
    _variable_name: List[UILabel]
    _target_label: UILabel
    _result_label: UILabel

    _hint_button: UIButton
    _new_button: UIButton

    def __init__(self) -> None:
        """

        """
        pygame.init()
        self._window_surface = pygame.display.set_mode((WIDTH, HEIGHT))
        self._manager = pygame.UIManager((UI_WIDTH, UI_HEIGHT))

        self._setup_puzzle()

        self._setup_ui()  # note, this helper creates some of the attributes

        self._is_running = False

    def _apply_hint(self, hint_vars: Dict[str, int]) -> None:
        """
        Apply the hint - this updates both the puzzle's variables
        and the values stored in the GUI's dropdown menus to be consistent
        with having updated one of the puzzle's variables to have the same
        value as the corresponding variable in <hint_vars>.
        """
        done = False
        for k in hint_vars:
            if not done and self._puzzle.variables[k] != hint_vars[k]:
                self._puzzle.variables[k] = hint_vars[k]
                self._tree.substitute({k: hint_vars[k]})
                del self._puzzle.variables[k]
                done = True

        self._redraw_puzzle()
        self._manager.clear_and_reset()
        self._setup_ui()

        # reset the UI dropdown menu items
        for i in range(len(self._variable_name)):
            self._variable_map[i].selected_option = str(
                self._puzzle.variables[self._variable_name[i].text])
        if self._puzzle.is_solved():
            self._result_label.set_text("SOLVED!")
        else:
            tree_evaluation = self._tree.eval(self._puzzle.variables)
            self._result_label.set_text("Current:"
                                        "" + str(tree_evaluation))

    def _update_dropdowns(self) -> None:
        """
        Update the puzzle's variables to be consistent with what is in the
        GUI's dropdown menus.
        """
        for i in range(len(self._variable_name)):
            self._puzzle.variables[
                self._variable_name[i].text] = int(
                    self._variable_map[i].selected_option)
            if self._puzzle.is_solved():
                self._result_label.set_text("SOLVED!")
            else:
                tree_evaluation = self._tree.eval(self._puzzle.variables)
                self._result_label.set_text("Eval:"
                                            "" + str(tree_evaluation))

    def _set_variable_to_zero(self) -> None:
        """
        Set one variable in the puzzle to zero so a hint can be generated.
        """
        done = False
        for k in self._puzzle.variables:
            if not done and self._puzzle.variables[k] != 0:
                self._puzzle.variables[k] = 0
                i = [nom.text for nom in
                     self._variable_name].index(k)
                self._variable_map[i].selected_option = '0'
                done = True

    def _get_hint(self) -> None:
        """
        Get a hint for the user.
        """
        success = False
        while not success:
            solver = BfsSolver()
            sol = solver.solve(self._puzzle)
            if sol:
                hint_vars = sol[:2][-1].variables
                self._apply_hint(hint_vars)
                success = True
            else:
                # automatically set a variable to zero
                self._set_variable_to_zero()

    def _process_event(self, event: Event) -> None:
        """
        Processes a pygame event - which will be one of:
            - the user quit
            - new button pressed
            - hint button pressed
            - dropdown menu item changed
        """
        if event.type == pygame.QUIT:
            self._is_running = False

        if event.type == pygame.USEREVENT:
            if event.user_type == pygame.UI_BUTTON_PRESSED:
                if event.ui_element == self._new_button:
                    # create a new puzzle

                    # redo the GUI...
                    self._setup_puzzle()
                    self._manager.clear_and_reset()

                    self._setup_ui()

                elif event.ui_element == self._hint_button:
                    self._get_hint()

            if event.user_type == pygame.UI_DROP_DOWN_MENU_CHANGED:
                self._update_dropdowns()

    def play_game(self) -> None:
        """
        Main loop for playing an expression tree puzzle in the GUI.
        """
        pygame.display.set_caption('Expression Tree Puzzle')
        clock = pygame.time.Clock()
        self._is_running = True

        while self._is_running:
            time_delta = clock.tick(10)
            for event in pygame.event.get():
                self._process_event(event)
                self._manager.process_events(event)
                # update the game's display
                self._manager.update(time_delta)
                white = (255, 255, 255)
                self._window_surface.fill(white)
                self._window_surface.blit(self._expr_img, (100, 0))
                self._manager.draw_ui(self._window_surface)
                pygame.display.update()

    def _redraw_puzzle(self) -> None:
        """
        Setup the image of the puzzle so it can be displayed.
        """
        visualize(self._tree, fname='./demo_tree')
        expr_img = pygame.image.load('demo_tree.png')
        self._expr_img = pygame.transform.scale(expr_img, (WIDTH - 100, HEIGHT))

    def _setup_puzzle(self) -> None:
        """
        Generate a random expression tree puzzle and create the image for it.
        This helper is called inside the __init__ and creates several of the
        private instance attributes. It is called again any time the puzzle
        to be solved is changed (the new button is pressed).
        """
        self._tree, lookup = generate_random_expression_tree()

        for k in lookup:
            lookup[k] = randint(1, 9)
        target = self._tree.eval(lookup)
        for k in lookup:
            lookup[k] = 0
        self._puzzle = ExpressionTreePuzzle(self._tree, target)

        self._redraw_puzzle()

    def _setup_ui(self) -> None:
        """
        Set up the UI components for the game.
        This helper is called inside the __init__ and creates several of the
        private instance attributes. It is called again any time the puzzle
        to be solved is changed.
        """
        self._variable_map = []
        self._variable_name = []

        n_variables = len(self._puzzle.variables)

        for vname in self._puzzle.variables:
            rect = pygame.Rect((UI_WIDTH // 2, UI_ITEM_HEIGHT
                                * len(self._variable_name)),
                               (UI_WIDTH // 2, UI_ITEM_HEIGHT))
            uidrop = UIDropDownMenu([str(x)
                                     for x in range(10)],
                                    relative_rect=rect,
                                    starting_option=str(
                                        self._puzzle.variables[vname]),
                                    manager=self._manager)
            self._variable_map.append(uidrop)

            rect = pygame.Rect((0, UI_ITEM_HEIGHT * len(self._variable_name)),
                               (UI_WIDTH // 2, UI_ITEM_HEIGHT))

            label = UILabel(relative_rect=rect,
                            text=vname,
                            manager=self._manager)

            self._variable_name.append(label)

        rect = pygame.Rect((0, UI_ITEM_HEIGHT * n_variables),
                           (UI_WIDTH, UI_ITEM_HEIGHT))
        # target label
        UILabel(relative_rect=rect, text=f"Target: {self._puzzle.target}",
                manager=self._manager)

        rect = pygame.Rect((0, UI_ITEM_HEIGHT * (n_variables + 1)),
                           (UI_WIDTH, UI_ITEM_HEIGHT))
        tree_evaluation = self._tree.eval(self._puzzle.variables)
        self._result_label = UILabel(relative_rect=rect,
                                     text=f"Current:"
                                          f" {tree_evaluation}",
                                     manager=self._manager)

        rect = pygame.Rect((0, UI_HEIGHT // 2), (UI_WIDTH // 2, UI_ITEM_HEIGHT))
        self._hint_button = UIButton(relative_rect=rect,
                                     text='HINT',
                                     manager=self._manager)

        rect = pygame.Rect((0, UI_HEIGHT // 2 + UI_ITEM_HEIGHT),
                           (UI_WIDTH // 2, UI_ITEM_HEIGHT))
        self._new_button = UIButton(relative_rect=rect,
                                    text='NEW',
                                    manager=self._manager)


if __name__ == '__main__':
    gui = ExpressionTreePuzzleGUI()
    gui.play_game()
