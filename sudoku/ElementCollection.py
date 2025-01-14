import logging

logger = logging.getLogger(__name__)

class ElementCollection:
    """
    Represents a collection of elements in a Sudoku grid (row, column, or sub-grid).
    """
    def __init__(self, id, type, grid):
        """
        Initializes an ElementCollection with an ID, type, and reference to the grid.
        
        Args:
            id (int): The ID of the collection.
            type (str): The type of the collection ("Row", "Col", or "SubGrid").
            grid (Grid): The reference to the Sudoku grid.
        """
        self.id = id
        self.type = type
        self.grid = grid
        self.elements = []
        
    def append_element(self, element):
        """
        Appends an element to the collection.
        
        Args:
            element (Element): The element to append.
        """
        self.elements.append(element)
        
    def checkIfAlreadySet(self, value):
        """
        Checks if a value is already set in the collection.
        
        Args:
            value (int): The value to check.
        
        Returns:
            bool: True if the value is already set, False otherwise.
        """
        alreadySet = False
        for element in self.elements.__iter__():
            if element.isFinalValue(value):
                alreadySet = True
                break
        return alreadySet
        
    def getRow(self, indx):
        """
        Gets the row index for a given element index in the collection.
        
        Args:
            indx (int): The element index.
        
        Returns:
            int: The row index.
        """
        if indx < 0 or indx > 8: logger.error("getRow: indx out of range %s", indx); exit()
        if self.type == "Row": return self.id
        elif self.type == "Col": return indx
        else:
            rowMult = self.id // 3
            rowAdd = indx // 3
            return rowMult * 3 + rowAdd
            
    def getCol(self, indx):
        """
        Gets the column index for a given element index in the collection.
        
        Args:
            indx (int): The element index.
        
        Returns:
            int: The column index.
        """
        if indx < 0 or indx > 8: logger.error("getCol: indx out of range %s", indx); exit()
        if self.type == "Col": return self.id
        elif self.type == "Row": return indx
        else:
            colMult = self.id % 3
            colAdd = indx % 3
            return colMult * 3 + colAdd

    def removeVal(self, val):
        """
        Removes a value from all elements in the collection.
        
        Args:
            val (int): The value to remove.
        """
        for indx in range(9):
            self.elements[indx].remove(val)
            
    def singleValueRule(self):
        """
        Applies the single value rule to the collection.
        It looks for values that can only be in one position in the collection.
        """
        singleValues = []
        for indx in range(9):
            if self.elements[indx].cardinality() == 1:
                singleVal = list(self.elements[indx].values.keys())[0]
                singleValues.append(singleVal)
                if not self.elements[indx].final:
                    logger.debug("SVR: setting %s %s, indx %s to %s", self.type, self.id, indx, singleVal)
                    self.grid.setValue(self.getRow(indx), self.getCol(indx), singleVal)

    def singlePossibleValueRule(self):
        """
        Applies the single possible value rule to the collection. Applies the single possible value rule to the collection. 
        It looks for values that can only be in one position in the collection.
        """
        possibleValues = {1:"", 2:"", 3:"", 4:"", 5:"", 6:"", 7:"", 8:"", 9:""}
        for indx in range(9):
            values = list(self.elements[indx].values.keys())
            final = self.elements[indx].final
            if final:
                continue
            for val in values.__iter__():
                if possibleValues[val] == "":
                    possibleValues[val] = indx
                elif possibleValues[val] != "":
                    possibleValues[val] = "x"
        for indx in range(1,10):
            value = possibleValues.get(indx)
            if value != "x" and value != "" and value != None:
                logger.debug("SPVR: %s %s", self.type, self.id)
                logger.debug("values: \n%s", str(self))
                logger.debug("computed SPVs: %s", possibleValues)
                logger.debug("SPVR in %s %s: %s can only be at position %s", self.type, self.id, indx, value)
                self.grid.setValue(self.getRow(value), self.getCol(value), indx)
    
    def nakedDoubleValueRule(self):
        """
        Applies the naked double value rule to the collection.
        2 elements in the collection have the same 2 possible values, 
        remove those values from all other elements.
        """
        doubleValues = {}
        foundOne = False
        for indx in range(9):
            if self.elements[indx].cardinality() == 2:
                valueList = list(self.elements[indx].values.keys())
                valueTuple = (valueList[0], valueList[1])
                existingValue = doubleValues.get(str(valueTuple))
                if existingValue == None:
                    doubleValues[str(valueTuple)] = 1
                else:
                    logger.debug("nDVR: in %s, %s found tuple %s", self.type, self.id, str(valueTuple))
                    doubleValues[str(valueTuple)] = existingValue+1
                    foundOne = True
        if foundOne:
            for doubleValueKey in doubleValues:
                if doubleValues[doubleValueKey] == 2:
                    for indx in range(len(self.elements)):
                        valueList = list(self.elements[indx].values.keys())
                        if not (len(valueList) == 2 and doubleValueKey != (valueList[0], valueList[1])):
                            self.elements[indx].remove(int(doubleValueKey[1]))
                            self.elements[indx].remove(int(doubleValueKey[4]))
                        logger.debug("nDVR: after removal: values are\n%s", str(self.elements[indx].values))
    
    def __str__(self):
        """
        Returns a string representation of the ElementCollection.
        
        Returns:
            str: A string representation of the collection.
        """
        return_string = ""
        for element in self.elements.__iter__():
            return_string += element.__str__() + "\n"
        return return_string
