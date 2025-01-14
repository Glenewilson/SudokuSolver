import unittest
import logging
from sudoku.Element import Element
from sudoku.ElementCollection import ElementCollection
from sudoku.SudokuV1 import Grid

logging.basicConfig(filename='SudokuSolver.log',
                    format='%(asctime)s %(message)s',
                    filemode='w',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)

class TestElementCollection(unittest.TestCase):

    def setUp(self):
        self.grid = Grid()
        self.element_collection = self.grid.Rows[0]

    def test_append_element(self):
        logger.debug("Testing append_element")
        self.assertEqual(len(self.element_collection.elements), 9)

    def test_check_if_already_set(self):
        logger.debug("Testing checkIfAlreadySet")
        self.element_collection.elements[0].set(5)
        self.element_collection.elements[0].final = True
        self.assertTrue(self.element_collection.checkIfAlreadySet(5))
        self.assertFalse(self.element_collection.checkIfAlreadySet(3))

    def test_get_row(self):
        logger.debug("Testing getRow")
        self.assertEqual(self.element_collection.getRow(0), 0)
        self.element_collection.type = "Col"
        self.assertEqual(self.element_collection.getRow(0), 0)
        self.element_collection.type = "SubGrid"
        self.assertEqual(self.element_collection.getRow(0), 0)

    def test_get_col(self):
        logger.debug("Testing getCol")
        self.assertEqual(self.element_collection.getCol(0), 0)
        self.element_collection.type = "Row"
        self.assertEqual(self.element_collection.getCol(0), 0)
        self.element_collection.type = "SubGrid"
        self.assertEqual(self.element_collection.getCol(0), 0)

    def test_remove_val(self):
        logger.debug("Testing removeVal")
        self.element_collection.removeVal(5)
        for element in self.element_collection.elements:
            self.assertNotIn(5, element.values)

    def test_single_value_rule(self):
        logger.debug("Testing singleValueRule")
        self.element_collection.elements[0].set(5)
        self.element_collection.singleValueRule()
        self.assertTrue(self.element_collection.elements[0].final)

    def test_single_possible_value_rule(self):
        logger.debug("Testing singlePossibleValueRule")
        for index in range(1, 9):
            self.element_collection.elements[index].remove(5)
        self.element_collection.singlePossibleValueRule()
        logger.debug(f"element 0 values are: {self.element_collection.elements[0].values}")
        self.assertTrue(self.element_collection.elements[0].values == {5: ""})

    def test_naked_double_value_rule(self):
        logger.debug("Testing nakedDoubleValueRule")
        self.element_collection.elements[0].values = {3: True, 5: True}
        self.element_collection.elements[1].values = {3: True, 5: True}
        self.element_collection.nakedDoubleValueRule()
        for element in self.element_collection.elements[2:]:
            self.assertNotIn(3, element.values)
            self.assertNotIn(5, element.values)

if __name__ == '__main__':
    unittest.main()
