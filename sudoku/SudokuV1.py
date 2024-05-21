import queue

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
    
WISH LIST
    * CLI - DONE!!
    * set command must check error conditions - DONE!!
    * read input file
    * better arrange rules
    * consider event queue
        * changes made in elements need to go into event queue
    * consider event log
        * possibly just the queue, but don't remove values?
    * think about strategy to support bifurcation
        * lowest priority, want to get all else done first.
"""

class Element:
    def __init__(self, row, column, eventQ):
        self.values = {1:"", 2:"", 3:"", 4:"", 5:"", 6:"", 7:"", 8:"", 9:""}
        self.final = False
        self.row = row
        self.column = column
        self.events = eventQ

    def set(self, value):
        if self.values.get(value) != None:
            self.values.clear()
            self.values.setdefault(value,"")
            # do this in the single value rule
            #self.final = True
            self.events.put(["set", self.row, self.column, value])
        else:
            print("ERROR: Value " + str(value) + " is not valid in " + str(self.row) + "," + str(self.column))

    def remove(self, value):
        #print("popping " + str(value))
        if len(self.values) != 1:
            if self.values.get(value) != None:
                self.values.pop(value)
                self.events.put(["remove", self.row, self.column, value])
        return

    def cardinality(self):
        return len(self.values)

    def member(self, value):
        return self.values.get(value) != None
    
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
    def __init__(self, id):
        self.id = id
        self.elements = []
        
    def append_element(self, element):
        self.elements.append(element)
       
    def singleValueRule(self):
        singleValues = []
        for indx in range(9):
            # if it is already final, than we have already processed this one.
            # CANT do above, there are 3 element collections. This will stop 2 of them from working.
            # Will have to live with possible duplication rule checks.
            if self.elements[indx].cardinality() == 1:
                singleValues.append(list(self.elements[indx].values.keys())[0])
                self.elements[indx].final = True
        for value in singleValues:
            print("removing value: " + str(value))
            for element in self.elements:
                element.remove(value) 
    
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
            self.Rows.append(ElementCollection(indx))
            self.Cols.append(ElementCollection(indx))
            self.SubGrid.append(ElementCollection(indx))
        # create all 81 elements
        # place them in the right row, column, and sub grid
        for row in range(9):
            for col in range(9):
                El = Element(row, col, self.events)
                self.Rows[row].append_element(El)
                self.Cols[col].append_element(El)
                self.SubGrid[self.subGridIndex(row,col)].append_element(El)

    def setValue(self, row, col, val):
        print("setValue: " + str(row) + "," + str(col) + " value: " + str(val))
        self.Rows[row].elements[col].set(val)
        #self.events.put(["setValue", row, col, val])
    
    def evaluate(self):
        while self.events.not_empty:
            try:
                event = self.events.get(block=False)
                print("evaluating: " + str(event))
                row = event[1]
                col = event[2]
                print("evaluating SVR for col " + str(col))
                self.Cols[col].singleValueRule()
                print("evaluating SVR for row " + str(row))
                self.Rows[row].singleValueRule()
                print("evaluating SVR for subgrid " + str(self.subGridIndex(row,col)))
                self.SubGrid[self.subGridIndex(row,col)].singleValueRule()
            except queue.Empty:
                break
    
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
        print("Grid: pretty_print")
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
    '''
    
    #SudGrid = Grid()
    #print(SudGrid)
    
    #SudGrid.setValue()
    setAValue()
    print(SudGrid.pretty_print())
    SudGrid.evaluate()
    print(SudGrid.pretty_print())

    '''    
    print("setting 1,1 to 5")
    SudGrid.setValue(1,1,5)
    #print(SudGrid)
    #print("\n")
    print(SudGrid.pretty_print())
    '''
    
    