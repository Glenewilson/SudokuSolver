import logging

class Element:
    """
    Represents an element in a Sudoku grid.
    """
    def __init__(self, row, column, eventQ, logger):
        """
        Initializes an Element with a row, column, event queue, and logger.
        
        Args:
            row (int): The row index of the element.
            column (int): The column index of the element.
            eventQ (queue.Queue): The event queue for logging changes.
            logger (logging.Logger): The logger for logging messages.
        """
        self.values = {1:"", 2:"", 3:"", 4:"", 5:"", 6:"", 7:"", 8:"", 9:""}
        self.final = False
        self.row = row
        self.column = column
        self.events = eventQ
        self.logger = logger

    def set(self, value):
        """
        Sets the element to a specific value.
        
        Args:
            value (int): The value to set (1-9).
        """
        if self.member(value):
            self.values.clear()
            self.values.setdefault(value,"")
            # log this change to the event queue
            self.events.put(["set", self.row, self.column, value])
            self.logger.debug("Element.set(): set %s, %s to %s", self.row, self.column, value)
        else:
            self.logger.error("Element.set(): Value %s is not valid in %s, %s", str(value), str(self.row), str(self.column))

    def remove(self, value):
        """
        Removes a value from the element.
        
        Args:
            value (int): The value to remove (1-9).
        """
        if self.cardinality() != 1:
            if self.member(value):
                self.values.pop(value)
                # log this change to the event queue
                self.events.put(["remove", self.row, self.column, value])
                self.logger.debug("Element.remove(): removed %s from %s, %s", value, self.row, self.column)
        return

    def cardinality(self):
        """
        Returns the number of possible values for the element.
        
        Returns:
            int: The number of possible values.
        """
        return len(self.values)

    def member(self, value):
        """
        Checks if a value is a possible value for the element.
        
        Args:
            value (int): The value to check.
        
        Returns:
            bool: True if the value is possible, False otherwise.
        """
        return self.values.get(value) != None
        
    def isFinalValue(self, value):
        """
        Checks if a value is the final value for the element.
        
        Args:
            value (int): The value to check.
        
        Returns:
            bool: True if the value is the final value, False otherwise.
        """
        if self.final and self.member(value):
            return True
        return False
    
    def printThird(self, third):
        """
        Prints a third of the element's possible values.
        
        Args:
            third (int): The third to print (1-3).
        
        Returns:
            str: A string representation of the third.
        """
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
        """
        Returns a string representation of the Element.
        
        Returns:
            str: A string representation of the element.
        """
        return f"{self.row},{self.column}: {list(self.values.keys())}"
