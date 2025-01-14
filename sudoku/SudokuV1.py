import queue
import logging
import csv
from .Element import Element
from .ElementCollection import ElementCollection

logger = logging.getLogger(__name__)

"""
This is some of the first musings on how to solve a sudoku puzzle.

Data store.
Sudoku is a 9x9 grid.
Each row and column is important.
Each 3x3 sub grid is important.
Each element in the 9x9 grid is part of a row, column, and sub grid.
Each element needs to track the 9 possible values (1-9)
Each element needs to:
    1. initialize to all 9 values
    2. remove, if present, a value
    3. tell how many values are left
    4. throw an error if values go to 0
    5. nicely print out values
    6. know row, column, and sub grid it is part of
    
"""

'''
Grid layout:
Col    0 1 2  3 4 5  6 7 8
      +------+------+------+
Row 0 | sub  | sub  | sub  |
Row 1 | grid | grid | grid |
Row 2 |  0   |  1   |  2   |
      +------+------+------+
Row 3 | sub  | sub  | sub  |
Row 4 | grid | grid | grid |
Row 5 |  3   |  4   |  5   |
      +------+------+------+
Row 6 | sub  | sub  | sub  |
Row 7 | grid | grid | grid |
Row 8 |  6   |  7   |  8   |
      +------+------+------+
'''
class Grid:
    """
    Represents a Sudoku grid and provides methods to manipulate and solve it.
    """
    def __init__(self):
        """
        Initializes an empty 9x9 Sudoku grid with rows, columns, and sub-grids.
        """
        self.Cols = []
        self.Rows = []
        self.SubGrid = []
        self.events = queue.Queue()
        # create empty grid
        for indx in range(9):
            self.Rows.append(ElementCollection(indx, "Row", self))
            self.Cols.append(ElementCollection(indx, "Col", self))
            self.SubGrid.append(ElementCollection(indx, "SubGrid", self))
        # create all 81 elements
        # place them in the right row, column, and sub grid
        for row in range(9):
            for col in range(9):
                el = Element(row, col, self.events)
                self.Rows[row].append_element(el)
                self.Cols[col].append_element(el)
                self.SubGrid[self.subGridIndex(row,col)].append_element(el)

    #
    # set any single element to a value
    # make sure doing the set does not break the single value rule for
    # any row, column or sub-grid.
    #
    def setValue(self, row, col, val):
        """
        Sets a value in the grid at the specified row and column.
        
        Args:
            row (int): The row index (0-8).
            col (int): The column index (0-8).
            val (int): The value to set (1-9).
        """
        if not isinstance(row, int) or not isinstance(col, int) or not isinstance(val, int):
            logger.error("Invalid input types: row, col, and val must be integers")
            return
        if row < 0 or row > 8: logger.error("row index out of range: %s", row); return
        if col < 0 or col > 8: logger.error("col index out of range: %s", col); return
        if val < 1 or val > 9: logger.error("val out of range: %s", val); return

        rowAlreadySet = self.Rows[row].checkIfAlreadySet(val)
        colAlreadySet = self.Cols[col].checkIfAlreadySet(val)
        sgAlreadySet = self.SubGrid[self.subGridIndex(row,col)].checkIfAlreadySet(val)
        if not rowAlreadySet and not colAlreadySet and not sgAlreadySet:
            self.Rows[row].elements[col].set(val)
            self.Rows[row].elements[col].final = True
        else:
            logger.error("cannot set %s, %s to %s", row, col, val)
            if rowAlreadySet: logger.error("row already has %s", val)
            if colAlreadySet: logger.error("col already has %s", val)
            if sgAlreadySet: logger.error("sub grid already has %s", val)
            return
            
        self.cleanUpFromSet(row, col, val)

    def cleanUpFromSet(self, row, col, val):
        """
        Removes a value from the rest of the row, column, and sub-grid after setting it.
        
        Args:
            row (int): The row index.
            col (int): The column index.
            val (int): The value to remove.
        """
        self.Rows[row].removeVal(val)
        self.Cols[col].removeVal(val)
        self.SubGrid[self.subGridIndex(row,col)].removeVal(val)    

    def isSolved(self):
        """
        Checks if the Sudoku grid is completely solved.
        
        Returns:
            bool: True if the grid is solved, False otherwise.
        """
        solved = True
        for col in self.Cols.__iter__():
            for element in col.elements.__iter__():
                if not element.final:
                    solved = False
                    break
        return solved
    
    #
    # this one only runs on sub-grids
    #
    # in any sub-grid, if one row or column is the only possibility for a value, then
    # that value possibility can be removed from the rest of the row or column.
    #
    def pointingPairsRule(self, subGrid):
        """
        Applies the pointing pairs rule to a sub-grid.
        
        Args:
            subGrid (ElementCollection): The sub-grid to apply the rule to.
        """
        if subGrid.type != "SubGrid":
            return
        
        # what rows or cols the values appear
        rows = {1:[0,0,0], 2:[0,0,0], 3:[0,0,0], 4:[0,0,0], 5:[0,0,0], 6:[0,0,0], 7:[0,0,0], 8:[0,0,0], 9:[0,0,0]}
        cols = {1:[0,0,0], 2:[0,0,0], 3:[0,0,0], 4:[0,0,0], 5:[0,0,0], 6:[0,0,0], 7:[0,0,0], 8:[0,0,0], 9:[0,0,0]}
    
        # create lists of how many times values appear in what rows and columns
        for indx in range(9):
            if subGrid.elements[indx].final: 
                continue
            row = indx // 3
            col = indx % 3
            valueList = list(subGrid.elements[indx].values.keys())
            for val in valueList.__iter__():
                rows[val][row] = rows[val][row] + 1
                cols[val][col] = cols[val][col] + 1

        logger.debug("grid %s", subGrid.id)
        logger.debug("PPR: rows: %s", rows)
        logger.debug("PPR: cols: %s", cols)

        # look for [>1,0,0] (in any order)
        rowPairs = {}
        colPairs = {}
        foundRow = False
        foundCol = False
        for indx in range(1,10):
            rowList = rows[indx]
            if rowList[0] == 0 and rowList[1] == 0 and rowList[2] > 1: rowPairs[indx] = 2; foundRow = True
            if rowList[0] == 0 and rowList[2] == 0 and rowList[1] > 1: rowPairs[indx] = 1; foundRow = True
            if rowList[1] == 0 and rowList[2] == 0 and rowList[0] > 1: rowPairs[indx] = 0; foundRow = True
            colList = cols[indx]
            if colList[0] == 0 and colList[1] == 0 and colList[2] > 1: colPairs[indx] = 2; foundCol = True
            if colList[0] == 0 and colList[2] == 0 and colList[1] > 1: colPairs[indx] = 1; foundCol = True
            if colList[1] == 0 and colList[2] == 0 and colList[0] > 1: colPairs[indx] = 0; foundCol = True

        logger.debug("PPR: rowPairs: %s", rowPairs)
        logger.debug("PPR: colPairs: %s", colPairs)
            
        # if pairs found, remove values from rows and columns
        for rowVal in rowPairs:
            rowIndex = (subGrid.id // 3) * 3 + rowPairs[rowVal]
            colIndex = subGrid.id % 3
            rowCollction = self.Rows[rowIndex]
            logger.debug("PPR: removing %s from row %s", rowVal, rowIndex)
            for indx in range(9):
                if indx // 3 != colIndex:
                    rowCollction.elements[indx].remove(rowVal)
        for colVal in colPairs:
            colIndex = (subGrid.id % 3) * 3 + colPairs[colVal]
            rowIndex = subGrid.id // 3
            colCollction = self.Cols[colIndex]
            logger.debug("PPR: removing %s from column %s", colVal, colIndex)
            for indx in range(9):
                if indx // 3 != rowIndex:
                    colCollction.elements[indx].remove(colVal)
    
    #
    # this is the rule evaluator that solves the puzzle.
    # there are two types of rules:
    #    1. reactive rules that respond to previous actions and need to process before any other rules
    #    2. search rules that need to go through the whole grid, and hopefully find new actions
    # the initial value setting of the grid are the first actions.
    # when no new actions are found the evaluation quits.
    # 
    def evaluate(self):
        """
        Evaluates the Sudoku grid and applies rules to solve it.
        """
        # check to see if solved. can exit early with some events left.
        while self.events.not_empty and not self.isSolved():
            try:
                #
                # Reactive Rules - rules that are tirggered by some other action
                #
                event = self.events.get(block=False)
                logger.debug("evaluating: %s", event)
                name = event[0]
                row = event[1]
                col = event[2]
                self.Cols[col].singleValueRule()
                self.Rows[row].singleValueRule()
                self.SubGrid[self.subGridIndex(row,col)].singleValueRule()
                                
            except queue.Empty:
                #
                # Searching Rules - rules that are not reactive and are looking for
                #                   conditions in the grid
                #

                #
                # Row Rules
                #
                for row in range(9):
                    self.Rows[row].singlePossibleValueRule()
                    self.Rows[row].nakedDoubleValueRule()

                #
                # Column Rules
                #
                for col in range(9):
                    self.Cols[col].singlePossibleValueRule()
                    self.Cols[col].nakedDoubleValueRule()

                #
                # Sub-Grid Rules
                #
                for indx in range(9):
                    self.SubGrid[indx].singlePossibleValueRule()
                    self.SubGrid[indx].nakedDoubleValueRule()

                    # for debug purposes
                    logger.debug("\n%s",self.pretty_print())
                    self.pointingPairsRule(self.SubGrid[indx])                
                    # for debug purposes
                    logger.debug("\n%s", self.pretty_print())

                # if no changes, quit
                if self.events.empty():                
                    break

        if self.isSolved():
            print("SOLVED IT!")
    
    def printCols(self):
        """
        Prints the columns of the Sudoku grid.
        
        Returns:
            str: A string representation of the columns.
        """
        return_string = ""
        for col in self.Cols.__iter__():
            return_string += str(col) + "\n"
        return return_string
        
    def printSubGrid(self):
        """
        Prints the sub-grids of the Sudoku grid.
        
        Returns:
            str: A string representation of the sub-grids.
        """
        return_string = ""
        for sub in self.SubGrid.__iter__():
            return_string += str(sub) + "\n"
        return return_string

    def pretty_print(self):
        """
        Prints the Sudoku grid in a pretty format.
        
        Returns:
            str: A string representation of the grid.
        """
        return_string = ""
        for row in self.Rows.__iter__():
            for indx in range(1,4):
                for elem in row.elements.__iter__():
                    return_string += elem.printThird(indx)
                return_string += "\n"
            return_string += "\n"
        return return_string
    
    def __str__(self):
        """
        Returns a string representation of the Sudoku grid.
        
        Returns:
            str: A string representation of the grid.
        """
        return_string = ""
        for row in self.Rows.__iter__():
            return_string += str(row) + "\n"
        return return_string
    
    def subGridIndex(self, row, col):
        """
        Computes the sub-grid index for a given row and column.
        
        Args:
            row (int): The row index.
            col (int): The column index.
        
        Returns:
            int: The sub-grid index.
        """
        indx = col // 3 + 3 * (row // 3)
        return indx

    def load_grid(self, filepath):
        """
        Loads a Sudoku grid from a CSV file.
        
        Args:
            filepath (str): The path to the CSV file.
        """
        if not isinstance(filepath, str):
            logger.error("Invalid input type: filepath must be a valid file path")
            return
        try:
            with open(filepath, mode='r') as file:
                csv_reader = csv.reader(file)
                for row in csv_reader:
                    if len(row) != 3:
                        logger.error("Invalid row in CSV file: %s", row)
                        continue
                    if (row[0] > 9 or row[0] < 1) or (row[1] > 9 or row[1] < 1) or (row[2] > 9 or row[2] < 1):
                        logger.error("Invalid value in CSV file: %s", row)
                        continue
                    try:
                        r, c, v = int(row[0]), int(row[1]), int(row[2])
                        self.setValue(r - 1, c - 1, v)
                    except ValueError as e:
                        logger.error("Error parsing row %s: %s", row, e)
        except FileNotFoundError as e:
            logger.error("File not found: %s", e)
