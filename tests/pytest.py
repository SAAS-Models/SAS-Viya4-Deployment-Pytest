"""Tests for calculator module."""

import pytest
from src.calculator import add, subtract, multiply, divide


class TestCalculator:
    """Test calculator functions."""
    
    def test_add(self):
        """Test addition."""
        assert add(2, 3) == 5
        assert add(-1, 1) == 0
        assert add(0, 0) == 0
    
    def test_subtract(self):
        """Test subtraction."""
        assert subtract(5, 3) == 2
        assert subtract(0, 5) == -5
        assert subtract(10, 10) == 0
    
    def test_multiply(self):
        """Test multiplication."""
        assert multiply(3, 4) == 12
        assert multiply(-2, 3) == -6
        assert multiply(0, 100) == 0
    
    def test_divide(self):
        """Test division."""
        assert divide(10, 2) == 5
        assert divide(9, 3) == 3
        assert divide(7, 2) == 3.5
    
    def test_divide_by_zero(self):
        """Test that dividing by zero raises ValueError."""
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            divide(10, 0)
