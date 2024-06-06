import queue
import logging

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

class Element:
    def __init__(self, row, column, eventQ):
        self.values = {1:"", 2:"", 3:"", 4:"", 5:"", 6:"", 7:"", 8:"", 9:""}
        self.final = False
        self.row = row
        self.column = column
        self.events = eventQ

    def set(self, value):
        if self.member(value):
            self.values.clear()
            self.values.setdefault(value,"")
            # do this in the single value rule
            #self.final = True
            self.events.put(["set", self.row, self.column, value])
            logger.debug("Element.set(): set %s, %s to %s", self.row, self.column, value)
        else:
            logger.error("Element.set(): Value %s is not valid in %s, %s", str(value), str(self.row), str(self.column))

    def remove(self, value):
        #print("popping " + str(value))
        if self.cardinality() != 1:
            if self.member(value):
                self.values.pop(value)
                self.events.put(["remove", self.row, self.column, value])
                logger.debug("Element.remove(): removed %s from %s, %s", value, self.row, self.column)
        return

    def cardinality(self):
        return len(self.values)

    def member(self, value):
        return self.values.get(value) != None
        
    def isFinalValue(self, value):
        if self.final and self.member(value):
            return True
        return False
    
    # third - which third to print out
    #         valid range: 1-3
    # if value is final, print out that value in the center
    def printThird(self, third):
        upperRange = third * 3
        return_string = ""
        if self.final:
            if third == 2:
                finalVal = self.values.popitem()[0]
                return_string += "*" + str(finalVal) + "*"
                self.values.setdefault(finalVal,"")
            else:
                return_string += "   "
        else:
            for val in range(upperRange-2,upperRange+1):
                if self.member(val):
                    return_string += str(val)
                else:
                    return_string += " "
        return_string += " "
        return return_string

    def __str__(self):
        return f"{self.row},{self.column}: {list(self.values.keys())}"

class ElementCollection:
    def __init__(self, id, type, grid):
        self.id = id
        self.type = type
        self.grid = grid
        self.elements = []
        
    def append_element(self, element):
        self.elements.append(element)
        
    def checkIfAlreadySet(self, value):
        alreadySet = False
        for element in self.elements.__iter__():
            if element.isFinalValue(value):
                alreadySet = True
                break
        return alreadySet
        
    def getRow(self, indx):
        if indx < 0 or indx > 8: logger.error("getRow: indx out of range %s", indx); exit()
        if self.type == "Row": return self.id
        elif self.type == "Col": return indx
        else:
            rowMult = self.id // 3
            rowAdd = indx // 3
            return rowMult * 3 + rowAdd
            
    def getCol(self, indx):
        if indx < 0 or indx > 8: logger.error("getCol: indx out of range %s", indx); exit()
        if self.type == "Col": return self.id
        elif self.type == "Row": return indx
        else:
            colMult = self.id % 3
            colAdd = indx % 3
            return colMult * 3 + colAdd
    
    # an element has only one possible value left   
    def singleValueRule(self):
        singleValues = []
        for indx in range(9):
            # if it is already final, than we have already processed this one.
            # CANT do above, there are 3 element collections. This will stop 2 of them from working.
            # Will have to live with possible duplication rule checks.
            if self.elements[indx].cardinality() == 1:
                singleVal = list(self.elements[indx].values.keys())[0]
                singleValues.append(singleVal)
                if not self.elements[indx].final:
                    logger.debug("SVR: setting %s %s, indx %s to %s", self.type, self.id, indx, singleVal)
                    self.grid.setValue(self.getRow(indx), self.getCol(indx), singleVal)
        for value in singleValues:
            logger.debug("removing value: %s", value)
            for element in self.elements:
                element.remove(value) 
    
    # a row, col or sub-grid has a value possible in only one location
    def singlePossibleValueRule(self):
        #print("SPVR for ", self.type, " ", self.id)
        # possibleValue: for each possible value (1-9), mark in which position found
        # if value found in more than one position, mark with "x"
        possibleValues = {1:"", 2:"", 3:"", 4:"", 5:"", 6:"", 7:"", 8:"", 9:""}
        # find single values
        for indx in range(9):
            values = list(self.elements[indx].values.keys())
            final = self.elements[indx].final
            #print("indx: ", indx, " values: ", values, " final: ", final)
            if final:
                continue
            for val in values.__iter__():
                if possibleValues[val] == "":
                    possibleValues[val] = indx
                elif possibleValues[val] != "":
                    possibleValues[val] = "x"
        # mark the single values
        for indx in range(1,10):
            value = possibleValues.get(indx)
            if value != "x" and value != "" and value != None:
                #print(self.type, self.id, str(self))
                #print("computed SPVs: ", possibleValues)
                #print("SPVR in ", self.type, ", ", self.id, ", ", indx, " can only be at position ", value)
                logger.debug("SPVR: %s %s", self.type, self.id)
                logger.debug("values: \n%s", str(self))
                logger.debug("computed SPVs: %s", possibleValues)
                logger.debug("SPVR in %s %s: %s can only be at position %s", self.type, self.id, indx, value)
                #self.elements[value].set(indx)
                self.grid.setValue(self.getRow(value), self.getCol(value), indx)
    
    # a row, col, or sub-grid has 2 elements with only the same 2 possible values left
    # remove those values from the rest of the row, col, or sub-grid
    def nakedDoubleValueRule(self):
        # dictionary key=str(double value tuple), value=# of occurences
        doubleValues = {}
        foundOne = False
        #print("in DVR")
        # find elements with 2 values
        for indx in range(9):
            if self.elements[indx].cardinality() == 2:
                valueList = list(self.elements[indx].values.keys())
                valueTuple = (valueList[0], valueList[1])
                #print("found element with these two values: " + str(valueTuple))
                #print("current doubleValues dict: " + str(doubleValues))
                existingValue = doubleValues.get(str(valueTuple))
                if existingValue == None:
                    #print("was the first time")
                    doubleValues[str(valueTuple)] = 1
                else:
                    logger.debug("nDVR: in %s, %s found tuple %s", self.type, self.id, str(valueTuple))
                    doubleValues[str(valueTuple)] = existingValue+1
                    foundOne = True
        # remove the two values from the rest of the elements
        if foundOne:
            #print("removing values " + str(valueTuple) + " from " + self.type + " " + str(self.id))
            for doubleValueKey in doubleValues:
                #print("doubleValueKey: ", doubleValueKey, " type: ", type(doubleValueKey))
                #print("doubleValues: ", doubleValues)
                if doubleValues[doubleValueKey] == 2:
                    for indx in range(len(self.elements)):
                        valueList = list(self.elements[indx].values.keys())
                        #print("element " + str(self.elements[indx].row) + "," + str(self.elements[indx].column) + " : " + str(self.elements[indx].values))
                        #print("valueList is " + str(valueList) + ", doubleValueKey is " + str(doubleValueKey))
                        if not (len(valueList) == 2 and doubleValueKey != (valueList[0], valueList[1])):
                            #print("removing " + str(doubleValueKey) + " from element")
                            # touple string is: "(a, b)"
                            # a = touple[1], b = touple[4]
                            self.elements[indx].remove(int(doubleValueKey[1]))
                            self.elements[indx].remove(int(doubleValueKey[4]))
                        logger.debug("after removal: values are\n%s", str(self.elements[indx].values))
    
    
    def __str__(self):
        return_string = ""
        for element in self.elements.__iter__():
            return_string += element.__str__() + "\n"
        return return_string

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
    def __init__(self):
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

    def setValue(self, row, col, val):
        if row < 0 or row > 8: logger.error("row index out of range: %s", row); exit()
        if col < 0 or col > 8: logger.error("col index out of range: %s", col); exit()
        if val < 1 or val > 9: logger.error("val out of range: %s", val); exit()
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
            exit()
        
    def isSolved(self):
        solved = True
        for col in self.Cols.__iter__():
            for element in col.elements.__iter__():
                if not element.final:
                    solved = False
                    break
        return solved
    
    # this one only runs on sub-grids
    def pointingPairsRule(self, subGrid):
        if subGrid.type != "SubGrid":
            return
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

        logger.debug("PPR: rows: %s", rows)
        logger.debug("PPR: cols: %s", cols)

        # look for [>1,0,0] (in any order)
        rowPairs = [0,0,0]
        colPairs = [0,0,0]
        foundRow = False
        foundCol = False
        for indx in range(1,10):
            rowList = rows[indx]
            if rowList[0] == 0 and rowList[1] == 0 and rowList[2] > 1: rowPairs[2] = indx; foundRow = True
            if rowList[0] == 0 and rowList[2] == 0 and rowList[1] > 1: rowPairs[1] = indx; foundRow = True
            if rowList[1] == 0 and rowList[2] == 0 and rowList[0] > 1: rowPairs[0] = indx; foundRow = True
            colList = cols[indx]
            if colList[0] == 0 and colList[1] == 0 and colList[2] > 1: colPairs[2] = indx; foundCol = True
            if colList[0] == 0 and colList[2] == 0 and colList[1] > 1: colPairs[1] = indx; foundCol = True
            if colList[1] == 0 and colList[2] == 0 and colList[0] > 1: colPairs[0] = indx; foundCol = True

        logger.debug("PPR: rowPairs: %s", rowPairs)
        logger.debug("PPR: colPairs: %s", colPairs)
            
        # if pairs found, remove values from rows and columns
        if foundRow:
            # compute row index
            rowIndex = (subGrid.id // 3) * 3
            rowVal = rowPairs[0]
            if rowPairs[1] > 0: rowIndex += 1; rowVal = rowPairs[1]
            elif rowPairs[2] > 0: rowIndex += 2; rowVal = rowPairs[2]
            colIndex = (subGrid.id % 3) * 3
            rowCollction = self.Rows[rowIndex]
            logger.debug("PPR: removing %s from row %s", rowVal, rowIndex)
            for indx in range(9):
                if indx >= rowIndex and indx < rowIndex + 3: continue
                else:
                    rowCollction.elements[indx].remove(rowVal)
        if foundCol:
            # compute col index and get value to remove
            colIndex = (subGrid.id % 3) * 3
            colVal = colPairs[0]
            if colPairs[1] > 0: colIndex += 1; colVal = colPairs[1]
            elif colPairs[2] > 0: colIndex += 2; colVal = colPairs[2]
            colIndex = (subGrid.id // 3) * 3
            colCollction = self.Cols[colIndex]
            logger.debug("PPR: removing %s from column %s", colVal, colIndex)
            for indx in range(9):
                if indx >= colIndex and indx < colIndex + 3: continue
                else:
                    colCollction.elements[indx].remove(colVal)
    
    def evaluate(self):
        # check to see if solved. can exit early with some events left.
        while self.events.not_empty and not self.isSolved():
            try:
                event = self.events.get(block=False)
                logger.debug("evaluating: %s", event)
                name = event[0]
                row = event[1]
                col = event[2]
                #print("evaluating SVR for col " + str(col))
                self.Cols[col].singleValueRule()
                #print("evaluating SVR for row " + str(row))
                self.Rows[row].singleValueRule()
                #print("evaluating SVR for subgrid " + str(self.subGridIndex(row,col)))
                self.SubGrid[self.subGridIndex(row,col)].singleValueRule()
                self.Cols[col].singlePossibleValueRule()
                self.Rows[row].singlePossibleValueRule()
                self.SubGrid[self.subGridIndex(row,col)].singlePossibleValueRule()
                self.Cols[col].nakedDoubleValueRule()
                self.Rows[row].nakedDoubleValueRule()
                self.SubGrid[self.subGridIndex(row,col)].nakedDoubleValueRule()
                self.pointingPairsRule(self.SubGrid[self.subGridIndex(row,col)])
            except queue.Empty:
                break
        if self.isSolved():
            print("SOLVED IT!")
    
    def printCols(self):
        return_string = ""
        for col in self.Cols.__iter__():
            return_string += str(col) + "\n"
        return return_string
        
    def printSubGrid(self):
        return_string = ""
        for sub in self.SubGrid.__iter__():
            return_string += str(sub) + "\n"
        return return_string

    def pretty_print(self):
        return_string = ""
        for row in self.Rows.__iter__():
            for indx in range(1,4):
                for elem in row.elements.__iter__():
                    return_string += elem.printThird(indx)
                return_string += "\n"
            return_string += "\n"
        return return_string
    
    def __str__(self):
        return_string = ""
        for row in self.Rows.__iter__():
            return_string += str(row) + "\n"
        return return_string
    
    # given row and column, comput which sub-grid you are in
    def subGridIndex(self, row, col):
        indx = col // 3 + 3 * (row // 3)
        return indx

#def setAValue(row, col, val):
def setAValue():
    row = 1 #click.prompt('row', type=click.INT)
    col = 1 #click.prompt('col', type=click.INT)
    val = 5 #click.prompt('val', type=click.INT)
    #print("in setAValue")
    SudGrid.setValue(row, col, val)
    #print(SudGrid.pretty_print())
    #print("exiting setAValue")

# creating a global variable
SudGrid = Grid()
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
    setAValue()
    print(SudGrid.pretty_print())
    SudGrid.evaluate()
    print(SudGrid.pretty_print())

    for subGrid in range(9):
        for indx in range(9):
            val = SudGrid.SubGrid[subGrid].getCol(indx)
            print("subgrid", subGrid, "indx", indx, "col is", val)
            val = SudGrid.SubGrid[subGrid].getRow(indx)
            print("subgrid", subGrid, "indx", indx, "row is", val)

    '''    
    print("setting 1,1 to 5")
    SudGrid.setValue(1,1,5)
    #print(SudGrid)
    #print("\n")
    print(SudGrid.pretty_print())
    '''
    
    