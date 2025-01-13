import unittest
from sudoku.Element import Element

class TestElement(unittest.TestCase):

    def setUp(self):
        self.element = Element(0, 0, None)

    def test_initial_values(self):
        self.assertEqual(len(self.element.values), 9)
        self.assertTrue(all(val in self.element.values for val in range(1, 10)))

    def test_remove_value(self):
        self.element.remove(5)
        self.assertNotIn(5, self.element.values)
        self.assertEqual(len(self.element.values), 8)

    def test_cardinality(self):
        self.assertEqual(self.element.cardinality(), 9)
        self.element.remove(5)
        self.assertEqual(self.element.cardinality(), 8)

    def test_set_value(self):
        self.element.set(3)
        self.assertEqual(self.element.values, {3: True})
        self.assertTrue(self.element.final)

    def test_is_final_value(self):
        self.element.set(3)
        self.assertTrue(self.element.isFinalValue(3))
        self.assertFalse(self.element.isFinalValue(4))

    def test_print_third(self):
        self.element.set(3)
        self.assertEqual(self.element.printThird(1), "   ")
        self.assertEqual(self.element.printThird(2), " 3 ")
        self.assertEqual(self.element.printThird(3), "   ")

if __name__ == '__main__':
    unittest.main()
