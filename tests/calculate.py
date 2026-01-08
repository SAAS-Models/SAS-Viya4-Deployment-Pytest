"""
Calculator Module
A simple calculator with basic arithmetic operations.
"""


class Calculator:
    """Calculator class with basic arithmetic operations."""
    
    def __init__(self):
        """Initialize calculator with zero result."""
        self.result = 0
    
    def add(self, a, b):
        """
        Add two numbers.
        
        Args:
            a: First number
            b: Second number
            
        Returns:
            Sum of a and b
        """
        self.result = a + b
        return self.result
    
    def subtract(self, a, b):
        """
        Subtract b from a.
        
        Args:
            a: First number
            b: Number to subtract
            
        Returns:
            Difference of a and b
        """
        self.result = a - b
        return self.result
    
    def multiply(self, a, b):
        """
        Multiply two numbers.
        
        Args:
            a: First number
            b: Second number
            
        Returns:
            Product of a and b
        """
        self.result = a * b
        return self.result
    
    def divide(self, a, b):
        """
        Divide a by b.
        
        Args:
            a: Numerator
            b: Denominator
            
        Returns:
            Quotient of a and b
            
        Raises:
            ValueError: If b is zero
        """
        if b == 0:
            raise ValueError("Cannot divide by zero")
        self.result = a / b
        return self.result
    
    def power(self, base, exponent):
        """
        Raise base to the power of exponent.
        
        Args:
            base: Base number
            exponent: Exponent
            
        Returns:
            base raised to the power of exponent
        """
        self.result = base ** exponent
        return self.result
    
    def square_root(self, number):
        """
        Calculate square root of a number.
        
        Args:
            number: Number to calculate square root of
            
        Returns:
            Square root of the number
            
        Raises:
            ValueError: If number is negative
        """
        if number < 0:
            raise ValueError("Cannot calculate square root of negative number")
        self.result = number ** 0.5
        return self.result
    
    def get_result(self):
        """
        Get the last calculation result.
        
        Returns:
            Last calculation result
        """
        return self.result
    
    def clear(self):
        """Reset the calculator result to zero."""
        self.result = 0


# Helper functions for direct use without class instantiation
def add(a, b):
    """Add two numbers."""
    return a + b


def subtract(a, b):
    """Subtract b from a."""
    return a - b


def multiply(a, b):
    """Multiply two numbers."""
    return a * b


def divide(a, b):
    """Divide a by b."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


def power(base, exponent):
    """Raise base to the power of exponent."""
    return base ** exponent


def square_root(number):
    """Calculate square root of a number."""
    if number < 0:
        raise ValueError("Cannot calculate square root of negative number")
    return number ** 0.5
