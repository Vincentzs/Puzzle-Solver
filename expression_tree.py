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

This module contains the expression tree class.
"""

from __future__ import annotations

from typing import List, Dict, Optional, Tuple, Union

# for the provided tree visualization code
import matplotlib.pyplot as plt
import networkx as nx

# You may remove this import if you don't use it in your code.
from adts import Queue

# constants for the supported operators
OP_MULTIPLY = '*'
OP_ADD = '+'
OPERATORS = [OP_ADD, OP_MULTIPLY]


class ExprTree:
    """
    A tree representing an arithmetic expression.

    This class supports operators(+ and *), variables, and integer constants.

    === Private Attributes ===
    _root: The item stored at this tree's root, or None if the tree is empty.
    _subtrees: The list of all subtrees of this expression tree.

    === Representation Invariants ===
    - If self._root is None then self._subtrees is an empty list.
      This setting of attributes represents an empty tree.

      Note: self._subtrees may be empty when self._root is not None.
      This setting of attributes represents a tree consisting of just one
      node.

    - _subtrees contains no empty trees.

    - if _root is an int or a variable (str), then _subtrees is an empty list.

    - if _root is an int it has a value between 1 and 9, inclusive.

    - if _root is a variable, it is a single character (a-z).

    - if _root is an operator ('+' or '*'), it must have at least two children.
    """
    _root: Optional[Union[str, int]]
    _subtrees: List[ExprTree]

    def __init__(self, root: Optional[Union[str, int]],
                 subtrees: List[ExprTree]) -> None:
        """Initialize a new ExprTree with the given root value
        and subtrees.

        If <root> is None, the tree is empty.
        Preconditions:
        - if <root> is None, then <subtrees> is empty.
        - if <root> is not None, then it is either an operator(+ or *),
          an int (1-9), or a variable (a-z).
        - if <root> is an operator, then subtrees has at least two children.
        - if <root> is not an operator, subtrees is an empty list.
        """
        self._root = root
        self._subtrees = subtrees

    def is_empty(self) -> bool:
        """Return whether this expression tree is empty.

        >>> t1 = ExprTree(None, [])
        >>> t1.is_empty()
        True
        >>> t2 = ExprTree(3, [])
        >>> t2.is_empty()
        False
        """
        return self._root is None

    # TO DO (Task 4): implement eval
    def eval(self, lookup: Dict[str, int]) -> int:
        """
        Evaluate this expression tree and return the result.

        Precondition:
        lookup contains all of the variables necessary to evaluate
        this expression tree.

        >>> exp_t = ExprTree('+', [ExprTree(3, []), \
                                   ExprTree('*', [ExprTree('x', []), \
                                                  ExprTree('y', [])]), \
                                   ExprTree('x', [])])
        >>> look_up = {}
        >>> exp_t.populate_lookup(look_up)
        >>> look_up['x'] == 0
        True
        >>> exp_t.eval(look_up)
        3
        >>> look_up['x'] = 7
        >>> look_up['y'] = 3
        >>> exp_t.eval(look_up)
        31
        """
        if self.is_empty():
            return 0
        elif not self._subtrees:
            if isinstance(self._root, str):
                return lookup[self._root]
            else:
                return self._root
        else:
            if self._root == '*':
                val = 1
                for item in self._subtrees:
                    val *= item.eval(lookup)
            else:
                val = 0
                for item in self._subtrees:
                    val += item.eval(lookup)
            return val

    # TO DO (Task 4): implement __str__
    def __str__(self) -> str:
        """
        Return a string representation of this expression tree

        >>> exp_t = ExprTree('+', [ExprTree('a', []), \
                                   ExprTree('b', []), \
                                   ExprTree(3, [])])
        >>> str(exp_t) == '(a + b + 3)'
        True
        >>> exp_t = ExprTree(None, [])
        >>> str(exp_t) == '()'
        True
        >>> exp_t = ExprTree(5, [])
        >>> str(exp_t) == '5'
        True
        >>> exp_t = ExprTree('+', [ExprTree('*', [ExprTree(7, []), \
                                                  ExprTree('+', \
                                                           [ExprTree(6, []), \
                                                           ExprTree(6, [])] \
                                                          )]), \
                                   ExprTree(5, [])])
        >>> print(exp_t)
        ((7 * (6 + 6)) + 5)
        >>> exp_t = ExprTree('+', [ExprTree(3, []), \
                                   ExprTree('*', [ExprTree('x', []), \
                                                  ExprTree('y', [])]), \
                                   ExprTree('x', [])])
        >>> print(exp_t)
        (3 + (x * y) + x)
        """
        if self.is_empty():
            return '()'
        elif not self._subtrees:
            return str(self._root)
        else:
            lst = []
            for item in self._subtrees:
                lst.append(str(item))

            operator = f' {self._root} '
            return '(' + operator.join(lst) + ')'

    # TO DO (Task 4): implement __eq__
    def __eq__(self, other: ExprTree) -> bool:
        """
        Return whether this ExprTree is equivalent to <other>.

        Two expression tree's are equivalent if their _root attributes are
        equal and their _subtrees are all equal.

        >>> t1 = ExprTree(5, [])
        >>> t1 == ExprTree(5, [])
        True
        >>> t2 = ExprTree('*', [ExprTree(5, []), ExprTree(2, [])])
        >>> t2 == ExprTree('*', [ExprTree(5, []), ExprTree(2, [])])
        True
        >>> t2 == ExprTree('*', [])
        False
        >>> ExprTree('*', []) == ExprTree(None, [])
        False
        >>> t3 = ExprTree('*', [ExprTree(5, []), ExprTree(2, []),
        ...                     ExprTree(2, [])])
        >>> t2 == t3
        False
        >>> t4 = ExprTree('*', [ExprTree(5, []),
        ...                     ExprTree('*', [ExprTree(5, [])])])
        >>> t5 = ExprTree('*', [ExprTree(5, []),
        ...                     ExprTree('*', [ExprTree(2, [])])])
        >>> t4 == t5
        False
        """
        if self.is_empty() and other.is_empty():
            return True
        elif self._root != other._root or \
                len(self._subtrees) != len(other._subtrees):
            return False
        else:
            index = 0
            sub = self._subtrees
            other_sub = other._subtrees
            while index < len(sub):
                if sub[index] != other_sub[index]:
                    return False
                index += 1

            return True

    # TO DO (Task 4): implement substitute
    def substitute(self, from_to: Dict[Union[str, int],
                                       Union[str, int]]) -> None:
        """
        Replace each value in this expression tree that is a key in <from_to>
        with the value associated with it in <from_to>.

        Precondition:
        the key-value pairs in <from_to> will result
        in this expression tree still being a valid expression tree.

        >>> exp_t = ExprTree('a', [])
        >>> exp_t.substitute({'a': 1})
        >>> print(exp_t)
        1
        >>> exp_t = ExprTree('*',[ExprTree('a', []), \
                                 ExprTree('*', [ExprTree('a', []),\
                                                ExprTree(1, [])])])
        >>> exp_t.substitute({'a': 2, '*': '+'})
        >>> print(exp_t)
        (2 + (2 + 1))
        """
        if self.is_empty():
            return None
        else:
            if self._root in from_to:
                self._root = from_to[self._root]
            for item in self._subtrees:
                item.substitute(from_to)
            return None

    # TO DO (Task 4): implement populate_lookup
    def populate_lookup(self, lookup: Dict[str, int]) -> None:
        """
        Add entries to <lookup> so it contains a key for all variables
        appearing in this expression tree. Assign a value
        of 0 to each variable.

        >>> expr_t = ExprTree('a', [])
        >>> look_up = {}
        >>> expr_t.populate_lookup(look_up)
        >>> look_up['a'] == 0
        True
        >>> len(look_up) == 1
        True
        """
        if self.is_empty():
            return None
        elif not self._subtrees:
            if isinstance(self._root, str):
                lookup[self._root] = 0
        else:
            for item in self._subtrees:
                item.populate_lookup(lookup)
            return None
        return None

    def append(self, child: ExprTree) -> None:
        """Append child to this ExprTree's list of subtrees.

        Precondition: self is not an empty tree.

        >>> exp_t = ExprTree('+', [ExprTree('a', []), ExprTree(3, [])])
        >>> print(exp_t)
        (a + 3)
        >>> exp_t.append(ExprTree(5, []))
        >>> print(exp_t)
        (a + 3 + 5)
        """
        self._subtrees.append(child)

    def copy(self) -> ExprTree:
        """
        Return a copy of this ExprTree
        """
        if self.is_empty():
            return ExprTree(None, [])
        node = ExprTree(self._root, [])
        for c in self._subtrees:
            node._subtrees.append(c.copy())
        return node

    # Provided visualization code - see an example usage at the bottom
    # of this file in the __main__ block.
    def visualize(self, g: nx.Graph, maps: Tuple[Dict[str, str],
                                                 Dict[int, List[str]]],
                  path: str = '', depth: int = 0) -> None:
        """
        Helper for creating a visualization of this ExprTree using networkx
        and matplotlib.

        You do not need to understand this code.
        """
        label_map, at_depth = maps
        # record all nodes at each depth and create
        # nodes (with unique names) and edges in the networkx graph g.
        if depth not in at_depth:
            at_depth[depth] = []
        node_label = path + str(depth) + str(self._root)
        at_depth[depth].append(node_label)
        label_map[node_label] = str(self._root)
        g.add_node(node_label)
        i = 0
        for c in self._subtrees:
            # recursively call visualize on each subtree
            c.visualize(g, (label_map, at_depth),
                        path + str(i), depth + 1)
            # connect self to each of its children in the graph
            g.add_edge(node_label,
                       path + str(i) + str(depth + 1) + str(c._root))
            i += 1


# TO DO (Task 4): implement construct_from_list
def construct_from_list(values: List[List[Union[str, int]]]) -> ExprTree:
    """
    Construct an expression tree from <values>.

    See the handout for a detailed explanation of how <values>
    encodes the expression tree.

    Hint: We have provided you with the helper method ExprTree.append
          You will likely want to use this method.

    Precondition:
    <values> encodes a valid expression tree


    >>> example = [[5]]
    >>> exp_t = construct_from_list(example)
    >>> exp_t == ExprTree(5, [])
    True
    >>> print(exp_t)
    5
    >>> print(ExprTree(5, []))
    5
    >>> example = [['+'], [3, 'a']]
    >>> exp_t = construct_from_list(example)
    >>> subtrees = [ExprTree(3, []), ExprTree('a', [])]
    >>> exp_t == ExprTree('+', subtrees)
    True
    """
    if not values:
        return ExprTree(None, [])
    elif len(values) == 1:
        return ExprTree(values[0][0], [])

    expr_t = ExprTree(values[0][0], [])
    q = Queue()
    q.enqueue(expr_t)

    i = 1
    while not q.is_empty():
        curr_tree = q.dequeue()
        j = 0
        # for item in values[i]: Maybe index out of range?
        while i < len(values) and j < len(values[i]):
            sub_tree = ExprTree(values[i][j], [])
            curr_tree.append(sub_tree)
            if values[i][j] in OPERATORS:
                q.enqueue(sub_tree)
            j += 1
        i += 1
    return expr_t


# Provided visualization code - see an example usage at the bottom
# of this file in the __main__ block.
def visualize(tree: ExprTree,
              display: bool = False,
              fname: str = "./expr_tree_sample") -> None:
    """
    Create a visualization of the given <tree> using networkx and matplotlib.

    You do not need to understand this code, but may find it helpful to use
    it in order to visually see what the expression tree looks like.

    Providing the optional argument <display> set to True will display
    the resulting image.

    The image is saved to <fname>.png (see the default value for <fname> above)
    if <display> is False.
    """
    g = nx.Graph()
    labels = {}
    at_depth = {}
    # populate g based on the tree and collect information to
    # allow us to layout the tree visualization nicely
    tree.visualize(g, (labels, at_depth))

    # set position attribute for each tree node in the visualization,
    # based on how many nodes are at the same depth
    attrs = {}
    m = max([len(at_depth[d]) for d in at_depth])
    height = max(at_depth)
    for k in at_depth:
        nodes = at_depth[k]
        n = len(nodes)
        width = (n / m)
        for i in range(len(nodes)):
            if n == 1:
                loc = 0
            else:
                loc = -width + (2 * i * width / (n - 1))
            attrs[nodes[i]] = {'pos': (loc, -k / height)}

    nx.set_node_attributes(g, attrs)

    # change * to multiplication cross - unicode char u"\u00D7"
    for k in labels:
        labels[k] = labels[k].replace('*', u"\u00D7")

    _draw_graph(g, labels, fname, display)


def _draw_graph(g: nx.Graph,
                labels: Dict[str, str],
                fname: str,
                display: bool) -> None:
    """
    Helper function for visualize.

    Use matplotlib to visualize <g> with the given <labels>.

    If <display> is False, save the image to <fname>.
    Otherwise, show the matplotlib figure.
    """
    pos = nx.get_node_attributes(g, 'pos')
    plt.figure(figsize=(8, 6))
    # plot options
    options = {
        "font_size": 32,
        "node_size": 2800,
        "node_color": "white",
        "edgecolors": "black",
        "linewidths": 5,
        "width": 5,
    }
    nx.draw(g, pos,
            labels=labels,
            with_labels=True, font_weight='bold', **options)
    ax = plt.gca()
    ax.margins(0.10)
    plt.axis("off")
    if display:
        plt.show()
    else:
        plt.savefig(fname + ".png", dpi=300)
    plt.close()


if __name__ == "__main__":
    import python_ta

    python_ta.check_all(config={'pyta-reporter': 'ColorReporter',
                                'allowed-io': [],
                                'allowed-import-modules': ['doctest',
                                                           'python_ta',
                                                           'typing',
                                                           '__future__',
                                                           'matplotlib.pyplot',
                                                           'random',
                                                           'networkx',
                                                           'adts'],
                                'disable': ['E1136'],
                                'max-attributes': 15}
                        )

    # uncomment to generate example of expression tree from the handout
    # once you have completed the required parts of the code above

    # import doctest
    # doctest.testmod()

    # ex = [['+'], [3, '*', 'a', '+'], ['a', 'b'], [5, 'c']]
    # exprt = construct_from_list(ex)
    # visualize(exprt)  # , display=True)  # toggle display or save to file
