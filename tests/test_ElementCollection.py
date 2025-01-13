import unittest
from sudoku.Element import Element
from sudoku.ElementCollection import ElementCollection
from sudoku.SudokuV1 import Grid

class TestElementCollection(unittest.TestCase):

    def setUp(self):
        self.grid = Grid()
        self.element_collection = ElementCollection(0, "Row", self.grid)
        for i in range(9):
            self.element_collection.append_element(Element(0, i, None))

    def test_append_element(self):
        self.assertEqual(len(self.element_collection.elements), 9)

    def test_check_if_already_set(self):
        self.element_collection.elements[0].set(5)
        self.assertTrue(self.element_collection.checkIfAlreadySet(5))
        self.assertFalse(self.element_collection.checkIfAlreadySet(3))

    def test_get_row(self):
        self.assertEqual(self.element_collection.getRow(0), 0)
        self.element_collection.type = "Col"
        self.assertEqual(self.element_collection.getRow(0), 0)
        self.element_collection.type = "SubGrid"
        self.assertEqual(self.element_collection.getRow(0), 0)

    def test_get_col(self):
        self.assertEqual(self.element_collection.getCol(0), 0)
        self.element_collection.type = "Row"
        self.assertEqual(self.element_collection.getCol(0), 0)
        self.element_collection.type = "SubGrid"
        self.assertEqual(self.element_collection.getCol(0), 0)

    def test_remove_val(self):
        self.element_collection.elements[0].set(5)
        self.element_collection.removeVal(5)
        for element in self.element_collection.elements:
            self.assertNotIn(5, element.values)

    def test_single_value_rule(self):
        self.element_collection.elements[0].set(5)
        self.element_collection.singleValueRule()
        self.assertTrue(self.element_collection.elements[0].final)

    def test_single_possible_value_rule(self):
        self.element_collection.elements[0].set(5)
        self.element_collection.singlePossibleValueRule()
        self.assertTrue(self.element_collection.elements[0].final)

    def test_naked_double_value_rule(self):
        self.element_collection.elements[0].values = {3: True, 5: True}
        self.element_collection.elements[1].values = {3: True, 5: True}
        self.element_collection.nakedDoubleValueRule()
        for element in self.element_collection.elements[2:]:
            self.assertNotIn(3, element.values)
            self.assertNotIn(5, element.values)

if __name__ == '__main__':
    unittest.main()
