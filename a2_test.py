import unittest
from unittest.mock import patch
from sudoku_puzzle import *
from solver import *
from word_ladder_puzzle import *
from expression_tree import *
from expression_tree_puzzle import *


class TestUtil(unittest.TestCase):
    def assertSoduku(self, exp, sudoku):
        self.assertEqual(exp, sudoku)

    def assertLadder(self, exp, ladder):
        self.assertEqual(exp, ladder)


class Part1Test(TestUtil):
    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    def test_failfast_all_empty(self):
        """
        You cannot immediately determine the dead end of an empty board
        """
        sudoku = SudokuPuzzle(4, [[EMPTY_CELL for _ in range(4)] for _ in
                                  range(4)], {str(i) for i in range(1, 5, 1)})
        res = sudoku.fail_fast()
        self.assertFalse(res)

    def test_fail_fast_with_in_row(self):
        """
        -------
        |24|  |
        |  |13|
        -------
        |  |  |
        |  |  |
        -------
        For the row 1 the only choice you have is 13 which resist in the same
        square
        """
        sudoku = SudokuPuzzle(4, [['2', '4', EMPTY_CELL, EMPTY_CELL],
                                  [EMPTY_CELL, EMPTY_CELL, '1', '3'],
                                  [EMPTY_CELL] * 4,
                                  [EMPTY_CELL] * 4],
                              {str(i) for i in range(1, 5, 1)})
        res = sudoku.fail_fast()
        self.assertTrue(res)

    def test_fail_fast_with_in_square(self):
        """
        -------
        |1 |  |
        |34|  |
        -------
        | 2|  |
        |  |  |
        -------
        For the first sub-square you can the only remaining one is 2 but it lies
        on the same column
        """
        sudoku = SudokuPuzzle(4, [['1', EMPTY_CELL, EMPTY_CELL, EMPTY_CELL],
                                  ['3', '4', EMPTY_CELL, EMPTY_CELL],
                                  [EMPTY_CELL, '2', EMPTY_CELL, EMPTY_CELL],
                                  [EMPTY_CELL] * 4],
                              {str(i) for i in range(1, 5, 1)})
        res = sudoku.fail_fast()
        self.assertTrue(res)

    def test_fail_fast_with_in_column(self):
        """
        -------
        |1 |  |
        |3 |  |
        -------
        | 2|  |
        | 4|  |
        -------
        For this first column you need to fill 24 which already appear in the
        same sub-square
        """
        sudoku = SudokuPuzzle(4, [['1', EMPTY_CELL, EMPTY_CELL, EMPTY_CELL],
                                  ['3', EMPTY_CELL, EMPTY_CELL, EMPTY_CELL],
                                  [EMPTY_CELL, '2', EMPTY_CELL, EMPTY_CELL],
                                  [EMPTY_CELL, '4', EMPTY_CELL, EMPTY_CELL],
                                  ], {str(i) for i in range(1, 5, 1)})
        res = sudoku.fail_fast()
        self.assertTrue(res)

    def test_fail_fast_non_rec(self):
        """
        -------
        | 1|  |
        |  |  |
        -------
        |2 |  |
        |4 |  |
        -------
        Although, in the end, this is an unsolvable board, but it requires at
        least two steps detection, in the current state, the top left one can
        still fill with 3, thus we cannot determine this will fail
        """
        sudoku = SudokuPuzzle(4,
                              [[EMPTY_CELL, '1', EMPTY_CELL, EMPTY_CELL],
                               [EMPTY_CELL, EMPTY_CELL, EMPTY_CELL, EMPTY_CELL],
                               ['2', EMPTY_CELL, EMPTY_CELL, EMPTY_CELL],
                               ['4', EMPTY_CELL, EMPTY_CELL, EMPTY_CELL], ],
                              {str(i) for i in range(1, 5, 1)})
        res = sudoku.fail_fast()
        self.assertFalse(res)


class Part2Test(TestUtil):
    def setUp(self) -> None:
        self.empty_board = SudokuPuzzle(4, [[EMPTY_CELL] * 4,
                                            [EMPTY_CELL] * 4,
                                            [EMPTY_CELL] * 4,
                                            [EMPTY_CELL] * 4],
                                        {str(i) for i in range(1, 5, 1)})
        self.board_4_4 = SudokuPuzzle(4,
                                      [['1'] + [EMPTY_CELL] * 3,
                                       [EMPTY_CELL] * 2 + ['2', EMPTY_CELL],
                                       [EMPTY_CELL, '3'] + [EMPTY_CELL] * 2,
                                       [EMPTY_CELL] * 4],
                                      {str(i) for i in range(1, 5, 1)})
        self.board_4_4_2 = SudokuPuzzle(4,
                                        [['1'] + [EMPTY_CELL] * 3,
                                         [EMPTY_CELL] * 3 + ['3'],
                                         [EMPTY_CELL, '4'] + ['2', EMPTY_CELL],
                                         [EMPTY_CELL] * 4],
                                        {str(i) for i in range(1, 5, 1)})
        self.board_9_9 = SudokuPuzzle(9,
                                      [['2', '8', '6', '1', '5', '9', '7', '4',
                                        '3'],
                                       ['3', '5', '7', '6', '4', '8', '2', '1',
                                        '9'],
                                       ['4', '1', '9', '7', EMPTY_CELL,
                                        EMPTY_CELL, '5', '6', '8'],
                                       ['8', '2', '1', '9', '6', '5', '4', '3',
                                        '7'],
                                       ['6', '9', '3', '8', '7', '4', '1', '2',
                                        '5'],
                                       ['7', '4', '5', '3', EMPTY_CELL,
                                        EMPTY_CELL, '8', '9', '6'],
                                       ['5', '6', '8', '2', EMPTY_CELL,
                                        EMPTY_CELL, '9', '7', '4'],
                                       ['1', '3', '4', '5', '9', '7', '6', '8',
                                        '2'],
                                       ['9', '7', '2', '4', '8', '6', '3', '5',
                                        '1']
                                       ], {str(i) for i in range(1, 10)})
        self.fail_board = SudokuPuzzle(4,
                                       [[EMPTY_CELL, '1', EMPTY_CELL,
                                         EMPTY_CELL],
                                        [EMPTY_CELL, EMPTY_CELL, EMPTY_CELL,
                                         EMPTY_CELL],
                                        ['2', EMPTY_CELL, EMPTY_CELL,
                                         EMPTY_CELL],
                                        ['4', EMPTY_CELL, EMPTY_CELL,
                                         EMPTY_CELL], ],
                                       {str(i) for i in range(1, 5, 1)})
        self.bfs_solver = BfsSolver()
        self.dfs_solver = DfsSolver()

    def tearDown(self) -> None:
        pass

    def test_bfs_result(self):
        res = self.bfs_solver.solve(self.board_4_4_2)
        self.assertTrue(len(res) == 13)
        exp = SudokuPuzzle(4,
                           [['1', '3', '4', '2'],
                            ['4', '2', '1', '3'],
                            ['3', '4', '2', '1'],
                            ['2', '1', '3', '4']],
                           {str(i) for i in range(1, 5, 1)})
        self.assertSoduku(str(exp), str(res[-1]))

    def test_bfs_result_2(self):
        res = self.bfs_solver.solve(self.fail_board)
        self.assertTrue(res == [])

    def test_bfs_result_3(self):
        res = self.bfs_solver.solve(self.empty_board)
        self.assertTrue(len(res) == 17)
        self.assertTrue(res[-1].is_solved())

    def test_bfs_result_4(self):
        sol = SudokuPuzzle(9, [['2', '8', '6', '1', '5', '9', '7', '4',
                                '3'],
                               ['3', '5', '7', '6', '4', '8', '2', '1',
                                '9'],
                               ['4', '1', '9', '7', '2', '3', '5', '6', '8'],
                               ['8', '2', '1', '9', '6', '5', '4', '3',
                                '7'],
                               ['6', '9', '3', '8', '7', '4', '1', '2',
                                '5'],
                               ['7', '4', '5', '3', '1', '2', '8', '9', '6'],
                               ['5', '6', '8', '2', '3', '1', '9', '7', '4'],
                               ['1', '3', '4', '5', '9', '7', '6', '8',
                                '2'],
                               ['9', '7', '2', '4', '8', '6', '3', '5',
                                '1']
                               ], {str(i) for i in range(1, 10)})
        res = self.bfs_solver.solve(self.board_9_9, {str(sol)})
        for _ in range(1000):
            self.assertTrue(len(res) == 7)
            self.assertTrue(res[-1].is_solved())
            self.assertSoduku(
                SudokuPuzzle(9, [['2', '8', '6', '1', '5', '9', '7', '4',
                                  '3'],
                                 ['3', '5', '7', '6', '4', '8', '2', '1',
                                  '9'],
                                 ['4', '1', '9', '7', '3', '2', '5', '6', '8'],
                                 ['8', '2', '1', '9', '6', '5', '4', '3',
                                  '7'],
                                 ['6', '9', '3', '8', '7', '4', '1', '2',
                                  '5'],
                                 ['7', '4', '5', '3', '2', '1', '8', '9', '6'],
                                 ['5', '6', '8', '2', '1', '3', '9', '7', '4'],
                                 ['1', '3', '4', '5', '9', '7', '6', '8',
                                  '2'],
                                 ['9', '7', '2', '4', '8', '6', '3', '5',
                                  '1']
                                 ], {str(i) for i in range(1, 10)}), res[-1])

    def test_dfs_result(self):
        res = self.dfs_solver.solve(self.board_4_4_2)
        self.assertTrue(len(res) == 13)
        exp = SudokuPuzzle(4,
                           [['1', '3', '4', '2'],
                            ['4', '2', '1', '3'],
                            ['3', '4', '2', '1'],
                            ['2', '1', '3', '4']],
                           {str(i) for i in range(1, 5, 1)})
        self.assertSoduku(str(exp), str(res[-1]))

    def test_dfs_result_2(self):
        res = self.dfs_solver.solve(self.fail_board)
        self.assertTrue(res == [])

    def test_dfs_result_3(self):
        res = self.dfs_solver.solve(self.empty_board)
        self.assertTrue(len(res) == 17)
        self.assertTrue(res[-1].is_solved())

    def test_dfs_result_4(self):
        sol = SudokuPuzzle(9, [['2', '8', '6', '1', '5', '9', '7', '4',
                                '3'],
                               ['3', '5', '7', '6', '4', '8', '2', '1',
                                '9'],
                               ['4', '1', '9', '7', '2', '3', '5', '6', '8'],
                               ['8', '2', '1', '9', '6', '5', '4', '3',
                                '7'],
                               ['6', '9', '3', '8', '7', '4', '1', '2',
                                '5'],
                               ['7', '4', '5', '3', '1', '2', '8', '9', '6'],
                               ['5', '6', '8', '2', '3', '1', '9', '7', '4'],
                               ['1', '3', '4', '5', '9', '7', '6', '8',
                                '2'],
                               ['9', '7', '2', '4', '8', '6', '3', '5',
                                '1']
                               ], {str(i) for i in range(1, 10)})
        res = self.dfs_solver.solve(self.board_9_9, {str(sol)})
        self.assertTrue(len(res) == 7)
        self.assertTrue(res[-1].is_solved())
        for _ in range(1000):
            self.assertSoduku(
                SudokuPuzzle(9, [['2', '8', '6', '1', '5', '9', '7', '4',
                                  '3'],
                                 ['3', '5', '7', '6', '4', '8', '2', '1',
                                  '9'],
                                 ['4', '1', '9', '7', '3', '2', '5', '6', '8'],
                                 ['8', '2', '1', '9', '6', '5', '4', '3',
                                  '7'],
                                 ['6', '9', '3', '8', '7', '4', '1', '2',
                                  '5'],
                                 ['7', '4', '5', '3', '2', '1', '8', '9', '6'],
                                 ['5', '6', '8', '2', '1', '3', '9', '7', '4'],
                                 ['1', '3', '4', '5', '9', '7', '6', '8',
                                  '2'],
                                 ['9', '7', '2', '4', '8', '6', '3', '5',
                                  '1']
                                 ], {str(i) for i in range(1, 10)}), res[-1])

    def test_unique_solution_1(self):
        """
        -------------
        |286|159|743|
        |357|648|219|
        |419|7  |568|
        -------------
        |821|965|437|
        |693|874|125|
        |745|3  |896|
        -------------
        |568|2  |974|
        |134|597|682|
        |972|486|351|
        -------------
        This actually has two solutions
        Solution 1
        -------------
        |286|159|743|
        |357|648|219|
        |419|723|568|
        -------------
        |821|965|437|
        |693|874|125|
        |745|312|896|
        -------------
        |568|231|974|
        |134|597|682|
        |972|486|351|
        -------------
        Solution 2
        -------------
        |286|159|743|
        |357|648|219|
        |419|732|568|
        -------------
        |821|965|437|
        |693|874|125|
        |745|321|896|
        -------------
        |568|213|974|
        |134|597|682|
        |972|486|351|
        -------------
        """
        self.assertFalse(self.board_9_9.has_unique_solution())

    def test_unique_solution_2(self):
        self.assertFalse(self.board_4_4.has_unique_solution())

    def test_unique_solution_3(self):
        self.assertTrue(self.board_4_4_2.has_unique_solution())

    def test_unique_solution_4(self):
        self.assertFalse(self.empty_board.has_unique_solution())

    def test_unique_solution_5(self):
        self.assertFalse(self.fail_board.has_unique_solution())


class Part3Test(TestUtil):
    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    def test_extension(self):
        ladder = WordLadderPuzzle('bb', 'cc',
                                  {'bb', 'bc', 'cc', 'ac', 'bcd', 'bbc'})
        ext = ladder.extensions()
        self.assertTrue(len(ext) == 1)
        self.assertLadder(WordLadderPuzzle('bc', 'cc',
                                           {'bb', 'bc', 'cc', 'ac', 'bcd',
                                            'bbc'}),
                          ext[-1])

    def test_extension_2(self):
        ladder = WordLadderPuzzle('bc', 'cc', {'bb', 'bc', 'cc'})
        act = ladder.extensions()
        self.assertTrue(len(act) == 2)
        exp = [WordLadderPuzzle('bb', 'cc', {'bb', 'bc', 'cc'}),
               WordLadderPuzzle('cc', 'cc', {'bb', 'bc', 'cc'})]
        self.assertTrue(act == exp or act == exp[::-1])

    def test_extension_3(self):
        ladder = WordLadderPuzzle('a', 'c',
                                  {'a', 'b', 'c', 'ab', 'ac', 'bc', 'abc'})
        act = ladder.extensions()
        self.assertTrue(len(act) == 2)
        exp = [WordLadderPuzzle('b', 'c',
                                {'a', 'b', 'c', 'ab', 'ac', 'bc', 'abc'}),
               WordLadderPuzzle('c', 'c',
                                {'a', 'b', 'c', 'ab', 'ac', 'bc', 'abc'})]
        self.assertTrue(act == exp or act == exp[::-1])

    def test_is_solved(self):
        ladder = WordLadderPuzzle('bb', 'cc', {'bb', 'bc', 'cc'})
        ext = ladder.extensions()[0]
        self.assertFalse(ext.is_solved())
        self.assertTrue(ext == WordLadderPuzzle('bc', 'cc', {'bb', 'bc', 'cc'}))
        ext2 = {x.from_word: x.is_solved() for x in ext.extensions()}
        self.assertDictEqual({'bb': False, 'cc': True}, ext2)

    def test_bfs_ladder(self):
        word_set = {'a', 'b', 'c', 'aa', 'ab', 'ac', 'ba', 'bb',
                    'bc', 'ca', 'cb', 'cc', 'aaa',
                    'aba', 'abc',
                    'aca', 'acb', 'acc'}
        ladder = WordLadderPuzzle('aaa', 'abc', word_set)
        bfs_solver = BfsSolver()
        act = bfs_solver.solve(ladder)
        acc = set()
        self.assertTrue(len(act) == 3)
        self.assertTrue(act[-1].is_solved())
        self.assertEqual([ladder, WordLadderPuzzle('aba', 'abc', word_set),
                          WordLadderPuzzle('abc', 'abc', word_set)], act)
        acc.add(str(act[-2]))
        act = bfs_solver.solve(ladder, acc)
        self.assertTrue(len(act) == 4)
        self.assertTrue(act[-1].is_solved())
        self.assertEqual([ladder, WordLadderPuzzle('aca', 'abc', word_set),
                          WordLadderPuzzle('acc', 'abc', word_set),
                          WordLadderPuzzle('abc', 'abc', word_set)], act)

    def test_dfs_ladder(self):
        word_set = {'a', 'b', 'c', 'aa', 'ab', 'ac', 'ba', 'bb',
                    'bc', 'ca', 'cb', 'cc', 'aaa',
                    'aba', 'abc',
                    'aca', 'acb', 'acc'}
        ladder = WordLadderPuzzle('aaa', 'abc', word_set)
        dfs_solver = DfsSolver()
        acc = {str(WordLadderPuzzle('aca', 'abc', word_set))}
        act = dfs_solver.solve(ladder, acc)
        self.assertTrue(len(act) == 3)
        self.assertTrue(act[-1].is_solved())
        self.assertEqual([ladder, WordLadderPuzzle('aba', 'abc', word_set),
                          WordLadderPuzzle('abc', 'abc', word_set)], act)
        acc = set()
        acc.add(str(act[-2]))
        acc.add(str(WordLadderPuzzle('acb', 'abc', word_set)))
        act = dfs_solver.solve(ladder, acc)
        self.assertTrue(len(act) == 4)
        self.assertTrue(act[-1].is_solved())
        self.assertEqual([ladder, WordLadderPuzzle('aca', 'abc', word_set),
                          WordLadderPuzzle('acc', 'abc', word_set),
                          WordLadderPuzzle('abc', 'abc', word_set)], act)

    @patch('solver.BfsSolver.solve', return_value=[1])
    def test_get_difficulty(self, mock_solver):
        ladder = WordLadderPuzzle('bb', 'cc', {'bb', 'bc', 'cc'})
        res = ladder.get_difficulty()
        self.assertTrue(mock_solver.called)
        self.assertTrue(res, TRIVIAL)

    @patch('solver.BfsSolver.solve', return_value=[1, 2, 3])
    def test_get_difficulty_2(self, mock_solver):
        ladder = WordLadderPuzzle('bb', 'cc', {'bb', 'bc', 'cc'})
        res = ladder.get_difficulty()
        self.assertTrue(mock_solver.called)
        self.assertTrue(res, EASY)

    @patch('solver.BfsSolver.solve', return_value=[1, 2, 3, 4])
    def test_get_difficulty_3(self, mock_solver):
        ladder = WordLadderPuzzle('bb', 'cc', {'bb', 'bc', 'cc'})
        res = ladder.get_difficulty()
        self.assertTrue(mock_solver.called)
        self.assertTrue(res, MEDIUM)

    @patch('solver.BfsSolver.solve', return_value=[1, 2, 3, 4, 5, 6])
    def test_get_difficulty_4(self, mock_solver):
        ladder = WordLadderPuzzle('bb', 'cc', {'bb', 'bc', 'cc'})
        res = ladder.get_difficulty()
        self.assertTrue(mock_solver.called)
        self.assertTrue(res, HARD)

    @patch('solver.BfsSolver.solve', return_value=[])
    def test_get_difficulty_5(self, mock_solver):
        ladder = WordLadderPuzzle('bb', 'cc', {'bb', 'bc', 'cc'})
        res = ladder.get_difficulty()
        self.assertTrue(mock_solver.called)
        self.assertTrue(res, IMPOSSIBLE)


class Part4Test(TestUtil):
    def setUp(self) -> None:
        self.leaf = ExprTree(1, [])
        self.single = ExprTree('+', [ExprTree(1, []), ExprTree(2, [])])
        self.chain = ExprTree('*', [ExprTree('a', []), ExprTree('b', [])])
        self.compound = ExprTree('*', [ExprTree('a', []), ExprTree('*', [
            ExprTree('a', []),
            ExprTree('*', [ExprTree('a', []), ExprTree('a', [])])])])
        self.compound_2 = ExprTree('*',
                                   [ExprTree('a', []),
                                    ExprTree('*',
                                             [ExprTree(
                                                 'b',
                                                 []),
                                                 ExprTree(
                                                     '*', [
                                                         ExprTree(
                                                             'c',
                                                             []),
                                                         ExprTree(
                                                             'd',
                                                             [])])])])
        self.compound_3 = ExprTree('*',
                                   [ExprTree('+',
                                             [ExprTree('+',
                                                       [ExprTree('a', []),
                                                        ExprTree('b', [])]),
                                              ExprTree('c', [])]),
                                    ExprTree('+',
                                             [ExprTree('d', []),
                                              ExprTree('+',
                                                       [ExprTree('e', []),
                                                        ExprTree('f', [])])])
                                    ])

    def tearDown(self) -> None:
        pass

    def test_eval_1(self):
        single = ExprTree(1, [])
        self.assertTrue(single.eval({}) == 1)

    def test_eval_2(self):
        single = ExprTree('+', [ExprTree(1, []), ExprTree(2, [])])
        self.assertTrue(single.eval({}) == 3)

    def test_eval_nested(self):
        env = {'a': 0, 'b': 0}
        nest = ExprTree('*', [ExprTree('a', []), ExprTree('b', [])])
        self.assertTrue(nest.eval(env) == 0)
        env['a'] = 1
        self.assertTrue(nest.eval(env) == 0)
        env['b'] = 2
        self.assertTrue(nest.eval(env) == 2)

    def test_eval_nested_2(self):
        nest = ExprTree('*', [ExprTree('a', []),
                              ExprTree('*',
                                       [ExprTree('a', []),
                                        ExprTree('*', [
                                            ExprTree('a',
                                                     []),
                                            ExprTree('a',
                                                     [])])])])
        self.assertTrue(nest.eval({'a': 1}) == 1)
        self.assertTrue(nest.eval({'a': 2}) == 2 ** 4)

    def test_eq_1(self):
        self.assertTrue(ExprTree(1, []) == ExprTree(1, []))

    def test_eq_2(self):
        self.assertTrue(ExprTree('+', [ExprTree(1, []), ExprTree(1, [])]) ==
                        ExprTree('+', [ExprTree(1, []), ExprTree(1, [])]))

    def test_substitute(self):
        tree = ExprTree(1, [])
        tree.substitute({'a': 1})
        self.assertTrue(str(tree) == '1')

    def test_substitute_2(self):
        tree = ExprTree('+', [ExprTree('a', []), ExprTree('b', [])])
        self.assertTrue(str(tree) == '(a + b)')
        tree.substitute({'a': 1})
        self.assertTrue(str(tree) == '(1 + b)')
        tree.substitute({'b': 2})
        self.assertTrue(str(tree) == '(1 + 2)')

    def test_substitute_3(self):
        nest = ExprTree('*', [ExprTree('a', []),
                              ExprTree('*',
                                       [ExprTree('b', []),
                                        ExprTree('*', [
                                            ExprTree('c',
                                                     []),
                                            ExprTree('d',
                                                     [])])])])
        self.assertTrue(str(nest) == '(a * (b * (c * d)))')
        nest.substitute({'a': 1})
        self.assertTrue(str(nest) == '(1 * (b * (c * d)))')
        nest.substitute({'b': 2})
        self.assertTrue(str(nest) == '(1 * (2 * (c * d)))')
        nest.substitute({'c': 3})
        self.assertTrue(str(nest) == '(1 * (2 * (3 * d)))')
        nest.substitute({'d': 4})
        self.assertTrue(str(nest) == '(1 * (2 * (3 * 4)))')
        nest.substitute({'*': '+'})
        self.assertTrue(str(nest) == '(1 + (2 + (3 + 4)))')

    def test_substitute_4(self):
        self.assertTrue(str(self.compound) == '(a * (a * (a * a)))')
        for i in range(1, 10):
            tree = self.compound.copy()
            tree.substitute({'a': i})
            self.assertTrue(str(tree) == f'({i} * ({i} * ({i} * {i})))')


    def test_lookup_1(self):
        a = {}
        self.leaf.populate_lookup(a)
        self.assertTrue(a == {})

    def test_lookup_2(self):
        a = {}
        self.single.populate_lookup(a)
        self.assertTrue(a == {})

    def test_lookup_3(self):
        a = {}
        self.compound.populate_lookup(a)
        self.assertTrue(a == {'a': 0})

    def test_lookup_4(self):
        a = {}
        self.compound_2.populate_lookup(a)
        self.assertTrue(a == {'a': 0, 'b': 0, 'c': 0, 'd': 0})

    def test_construct_1(self):
        start = [[1]]
        res = construct_from_list(start)
        self.assertTrue(res == ExprTree(1, []))

    def test_construct_2(self):
        start = [['+'], [1, 2]]
        res = construct_from_list(start)
        self.assertTrue(
            res == ExprTree('+', [ExprTree(1, []), ExprTree(2, [])]))

    def test_construct_3(self):
        start = [['*'], ['a', '*'], ['a', '*'], ['a', 'a']]
        res = construct_from_list(start)
        self.assertTrue(res == self.compound)

    def test_construct_4(self):
        start = [['*'], ['+', '+'], ['+', 'c'], ['d', '+'], ['a', 'b'],
                 ['e', 'f']]
        res = construct_from_list(start)
        self.assertTrue(res == self.compound_3)


class Part5Test(TestUtil):
    def setUp(self) -> None:
        self.leaf = ExprTree(1, [])
        self.single = ExprTree('+', [ExprTree(1, []), ExprTree(2, [])])
        self.chain = ExprTree('*', [ExprTree('a', []), ExprTree('b', [])])
        self.compound = ExprTree('*',
                                 [ExprTree('a', []),
                                  ExprTree('*', [
                                      ExprTree('a', []),
                                      ExprTree('*', [ExprTree('a', []),
                                                     ExprTree('a', [])])])])
        self.compound_2 = ExprTree('*',
                                   [ExprTree('a', []),
                                    ExprTree('*',
                                             [ExprTree(
                                                 'b',
                                                 []),
                                                 ExprTree(
                                                     '*', [
                                                         ExprTree(
                                                             'c',
                                                             []),
                                                         ExprTree(
                                                             'd',
                                                             [])])])])

    def tearDown(self) -> None:
        pass

    def test_is_solved(self):
        problem = ExpressionTreePuzzle(self.leaf, 1)
        self.assertTrue(problem.is_solved())

    def test_is_solved_2(self):
        problem = ExpressionTreePuzzle(self.single, 2)
        self.assertFalse(problem.is_solved())

    def test_is_solved_3(self):
        problem = ExpressionTreePuzzle(self.compound, 1)
        self.assertFalse(problem.is_solved())
        problem.variables = {'a': 1}
        self.assertTrue(problem.is_solved())

    def test_is_solved_4(self):
        problem = ExpressionTreePuzzle(self.compound_2, 1)
        self.assertFalse(problem.is_solved())
        problem.variables['a'] = 1
        self.assertFalse(problem.is_solved())
        problem.variables.update({'b': 1})
        self.assertFalse(problem.is_solved())
        problem.variables.update({'c': 1})
        self.assertFalse(problem.is_solved())
        problem.variables.update({'d': 1})
        self.assertTrue(problem.is_solved())
        problem.variables.update({'d': 2})
        self.assertFalse(problem.is_solved())

    def test_extension(self):
        problem = ExpressionTreePuzzle(self.leaf, 1)
        self.assertTrue(problem.extensions() == [])

    def test_extension_2(self):
        problem = ExpressionTreePuzzle(self.single, 1)
        self.assertTrue(problem.extensions() == [])

    def test_extension_3(self):
        problem = ExpressionTreePuzzle(self.compound, 1)
        ext = problem.extensions()
        self.assertTrue(len(ext) == 9)
        for sub in ext:
            self.assertTrue(len(sub.extensions()) == 0)

    def test_extension_4(self):
        problem = ExpressionTreePuzzle(self.compound_2, 1)
        ext = problem.extensions()
        self.assertTrue(len(ext) == 36)

    def test_extension_5(self):
        problem = ExpressionTreePuzzle(self.chain, 1)
        ext = problem.extensions()
        self.assertTrue(len(ext) == 18)
        for sub in ext:
            self.assertTrue(len(sub.extensions()) == 9)


if __name__ == '__main__':
    unittest.main(exit=False, verbosity=2)
