import queue
import logging
import csv
from .Element import Element
from .ElementCollection import ElementCollection

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
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        self.Cols = []
        self.Rows = []
        self.SubGrid = []
        self.events = queue.Queue()
        # create empty grid
        for indx in range(9):
            self.Rows.append(ElementCollection(indx, "Row", self, self.logger))
            self.Cols.append(ElementCollection(indx, "Col", self, self.logger))
            self.SubGrid.append(ElementCollection(indx, "SubGrid", self, self.logger))
        # create all 81 elements
        # place them in the right row, column, and sub grid
        for row in range(9):
            for col in range(9):
                el = Element(row, col, self.events, self.logger)
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
        if row < 0 or row > 8: self.logger.error("row index out of range: %s", row); exit()
        if col < 0 or col > 8: self.logger.error("col index out of range: %s", col); exit()
        if val < 1 or val > 9: self.logger.error("val out of range: %s", val); exit()

        rowAlreadySet = self.Rows[row].checkIfAlreadySet(val)
        colAlreadySet = self.Cols[col].checkIfAlreadySet(val)
        sgAlreadySet = self.SubGrid[self.subGridIndex(row,col)].checkIfAlreadySet(val)
        if not rowAlreadySet and not colAlreadySet and not sgAlreadySet:
            self.Rows[row].elements[col].set(val)
            self.Rows[row].elements[col].final = True
        else:
            self.logger.error("cannot set %s, %s to %s", row, col, val)
            if rowAlreadySet: self.logger.error("row already has %s", val)
            if colAlreadySet: self.logger.error("col already has %s", val)
            if sgAlreadySet: self.logger.error("sub grid already has %s", val)
            exit()
            
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

        self.logger.debug("grid %s", subGrid.id)
        self.logger.debug("PPR: rows: %s", rows)
        self.logger.debug("PPR: cols: %s", cols)

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

        self.logger.debug("PPR: rowPairs: %s", rowPairs)
        self.logger.debug("PPR: colPairs: %s", colPairs)
            
        # if pairs found, remove values from rows and columns
        for rowVal in rowPairs:
            rowIndex = (subGrid.id // 3) * 3 + rowPairs[rowVal]
            colIndex = subGrid.id % 3
            rowCollction = self.Rows[rowIndex]
            self.logger.debug("PPR: removing %s from row %s", rowVal, rowIndex)
            for indx in range(9):
                if indx // 3 != colIndex:
                    rowCollction.elements[indx].remove(rowVal)
        for colVal in colPairs:
            colIndex = (subGrid.id % 3) * 3 + colPairs[colVal]
            rowIndex = subGrid.id // 3
            colCollction = self.Cols[colIndex]
            self.logger.debug("PPR: removing %s from column %s", colVal, colIndex)
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
                self.logger.debug("evaluating: %s", event)
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
                    self.logger.debug("\n%s",self.pretty_print())
                    self.pointingPairsRule(self.SubGrid[indx])                
                    # for debug purposes
                    self.logger.debug("\n%s", self.pretty_print())

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

# utility function for unit testing
def setAValue(r, c, v):
    row = r-1
    col = c-1
    val = v
    SudGrid.setValue(row, col, val)

# creating a global variable
SudGrid = Grid()
logging.basicConfig(filename='SudokuV1Debug.log',
                    format='%(asctime)s %(message)s',
                    filemode='w')
logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    '''
    # some unit testing
    El1 = Element(1,1)
    print(El1)
    print(El1.cardinality())
    print("is 9 in element? ", {El1.member(9)})
    El1.remove(9)
    print(El1)
    print(El1.cardinality())
    print("is 9 in element? ", {El1.member(9)})
    El1.set(5)
    print("set to a value")
    print(El1)
    
    Row1 = ElementCollection(1)
    Row1.append_element(El1)
    print(Row1.elements[0])
    print(Row1)
    Row1.elements[0].remove(8)
    print(Row1)
    print(El1)
    
    mylist = ["a", "b"]
    mytuple = (mylist[0], mylist[1])
    
    print("mylist: " + str(mylist))
    print("mytupe: " + str(mytuple))
    
    mydict = {}
    myval = mydict.get(str(mytuple))
    print("myval: " + str(myval))
    mydict[str(mytuple)] = 1
    myval = mydict[str(mytuple)]
    print("myval: " + str(myval))
    '''
    
    #SudGrid = Grid()
    #print(SudGrid)
    
    #SudGrid.setValue()
    setAValue(1,1,3)
    setAValue(1,5,2)
    setAValue(1,9,1)
    setAValue(2,5,4)
    setAValue(3,2,5)
    setAValue(3,4,8)
    setAValue(4,2,3)
    setAValue(4,5,7)
    setAValue(4,7,6)
    setAValue(4,9,5)
    setAValue(5,2,6)
    setAValue(5,6,8)
    setAValue(5,7,2)
    setAValue(5,9,9)
    setAValue(6,1,5)
    setAValue(6,3,8)
    setAValue(6,4,1)
    setAValue(7,8,9)
    setAValue(8,2,1)
    setAValue(8,3,5)
    setAValue(8,6,7)
    setAValue(9,3,7)
    setAValue(9,4,9)
    setAValue(9,7,5)
    print(SudGrid.pretty_print())
    SudGrid.evaluate()
    print(SudGrid.pretty_print())

    '''
    for subGrid in range(9):
        for indx in range(9):
            val = SudGrid.SubGrid[subGrid].getCol(indx)
            print("subgrid", subGrid, "indx", indx, "col is", val)
            val = SudGrid.SubGrid[subGrid].getRow(indx)
            print("subgrid", subGrid, "indx", indx, "row is", val)
    
    print("setting 1,1 to 5")
    SudGrid.setValue(1,1,5)
    #print(SudGrid)
    #print("\n")
    print(SudGrid.pretty_print())
    '''

