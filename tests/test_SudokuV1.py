import unittest
import logging
import os
from sudoku import SudokuV1

logging.basicConfig(filename='SudokuSolver.log',
                    format='%(asctime)s %(message)s',
                    filemode='w',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

class TestGrid(unittest.TestCase):

    def setUp(self):
        self.grid = SudokuV1.Grid()

    def test_set_value(self):
        self.grid.setValue(0, 0, 5)
        self.assertTrue(self.grid.Rows[0].elements[0].isFinalValue(5))

    def test_is_solved(self):
        for row in range(9):
            for col in range(9):
                val = (row * 3 + row // 3 + col) % 9 + 1
                logger.debug(f"[test_is_solved] Setting {row},{col} to {val}")
                self.grid.setValue(row, col, val)
        self.assertTrue(self.grid.isSolved())

    def test_load_grid_and_solve(self):
        test_csv = "/Users/glenwilson/code/personal/SudokuSolver/tests/testDoubleValueRule.csv"
        self.grid.load_grid(test_csv)
        self.grid.evaluate()
        self.assertTrue(self.grid.isSolved())

if __name__ == '__main__':
    unittest.main()
