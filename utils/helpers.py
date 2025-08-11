"""Helper functions for the stock analysis app."""

import re
from typing import Optional
from config.settings import TAIWAN_BANK_STOCKS


def validate_stock_symbol(symbol: str) -> tuple[bool, Optional[str]]:
    """
    Validate Taiwan stock symbol format.
    
    Args:
        symbol: Stock symbol to validate
        
    Returns:
        tuple: (is_valid, cleaned_symbol)
    """
    if not symbol:
        return False, None
    
    # Remove spaces and convert to uppercase
    symbol = symbol.strip().upper()
    
    # Check if it's in format XXXX.TW or just XXXX
    if re.match(r'^\d{4}\.TW$', symbol):
        return True, symbol
    elif re.match(r'^\d{4}$', symbol):
        return True, f"{symbol}.TW"
    
    return False, None


def get_stock_name(symbol: str) -> Optional[str]:
    """
    Get the Chinese name of the stock from symbol.
    
    Args:
        symbol: Stock symbol (e.g., "2881.TW" or "2881")
        
    Returns:
        Stock name in Chinese or None if not found
    """
    # Extract the numeric part
    stock_code = symbol.replace('.TW', '').replace('.tw', '')
    return TAIWAN_BANK_STOCKS.get(stock_code)


def format_currency(amount: float, currency: str = "TWD") -> str:
    """
    Format currency amount for display.
    
    Args:
        amount: Amount to format
        currency: Currency code (default: TWD)
        
    Returns:
        Formatted currency string
    """
    if currency == "TWD":
        return f"NT$ {amount:,.2f}"
    return f"{amount:,.2f} {currency}"


def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """
    Calculate percentage change between two values.
    
    Args:
        old_value: Original value
        new_value: New value
        
    Returns:
        Percentage change
    """
    if old_value == 0:
        return 0
    return ((new_value - old_value) / old_value) * 100


def format_percentage(percentage: float) -> str:
    """
    Format percentage for display with appropriate color indication.
    
    Args:
        percentage: Percentage value
        
    Returns:
        Formatted percentage string
    """
    sign = "+" if percentage > 0 else ""
    return f"{sign}{percentage:.2f}%"