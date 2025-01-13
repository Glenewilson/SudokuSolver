import unittest
import os
from sudoku.SudokuV1 import Grid

class TestGrid(unittest.TestCase):

    def setUp(self):
        self.grid = Grid()

    def test_set_value(self):
        self.grid.setValue(0, 0, 5)
        self.assertTrue(self.grid.Rows[0].elements[0].isFinalValue(5))

    def test_is_solved(self):
        for row in range(9):
            for col in range(9):
                self.grid.setValue(row, col, (row * 3 + col) % 9 + 1)
        self.assertTrue(self.grid.isSolved())

if __name__ == '__main__':
    unittest.main()
