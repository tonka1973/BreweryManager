"""
Calculation Utilities for Brewery Management System

Contains formulas and calculations used throughout the application.
"""

import math


def calculate_abv_from_gravity(og, fg):
    """
    Calculate ABV using HMRC official formula: ABV = (OG - FG) × f

    Factor 'f' is determined by gravity difference according to HMRC guidelines.
    The gravity difference is calculated as (OG - FG) × 1000.

    Args:
        og (float): Original Gravity (e.g., 1.045)
        fg (float): Final Gravity (e.g., 1.010)

    Returns:
        float: ABV percentage (e.g., 4.5) or None if inputs invalid
               Result is rounded DOWN to 1 decimal place per HMRC duty requirements.

    Example:
        >>> calculate_abv_from_gravity(1.045, 1.010)
        4.4
        >>> # If calculation gives 7.59%, it becomes 7.5% for duty purposes

    Note:
        This uses the official HMRC formula for alcohol duty calculations.
        The factor lookup table is based on gravity difference ranges.
        HMRC requires rounding DOWN to nearest 1 decimal place (e.g., 7.59% → 7.5%).
    """
    if not og or not fg or og <= fg:
        return None

    # Calculate gravity difference (multiply by 1000 for lookup table)
    diff = (og - fg) * 1000

    # HMRC factor lookup table based on gravity difference
    if diff <= 6.9:
        factor = 0.125
    elif diff <= 10.4:
        factor = 0.126
    elif diff <= 17.2:
        factor = 0.127
    elif diff <= 26.1:
        factor = 0.128
    elif diff <= 36.0:
        factor = 0.129
    elif diff <= 46.5:
        factor = 0.130
    elif diff <= 57.1:
        factor = 0.131
    elif diff <= 67.9:
        factor = 0.132
    elif diff <= 78.8:
        factor = 0.133
    elif diff <= 89.7:
        factor = 0.134
    elif diff <= 100.7:
        factor = 0.135
    else:
        factor = 0.135

    # Calculate ABV: (OG - FG) × 1000 × factor
    abv = diff * factor

    # HMRC requirement: Round DOWN to 1 decimal place for duty purposes
    # Example: 7.59% becomes 7.5%, not 7.6%
    return math.floor(abv * 10) / 10
