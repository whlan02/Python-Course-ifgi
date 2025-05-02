class Calculator:

    # add two numbers
    def add(self, a, b):
        return a + b
    
    # subtract b from a
    def subtract(self, a, b):
        return a - b
    
    # multiply two numbers
    def multiply(self, a, b):
        return a * b
    
    # divide a by b
    def divide(self, a, b):
        if b == 0: # check if b is zero
            raise ZeroDivisionError("Cannot divide by zero")
        return a / b # return the result of the division