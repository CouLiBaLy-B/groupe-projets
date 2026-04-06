"""
Investment Calculator Module
Provides functions to calculate investment returns, compound interest, and other financial metrics.
"""

import math
from typing import Dict, List, Tuple


def compound_interest(principal: float, annual_rate: float, years: float, compound_frequency: int = 12) -> float:
    """
    Calculate compound interest with regular compounding.

    Args:
        principal: Initial investment amount
        annual_rate: Annual interest rate (as percentage, e.g., 5 for 5%)
        years: Number of years to invest
        compound_frequency: How often interest is compounded (12 = monthly, 1 = yearly)

    Returns:
        Final amount after interest
    """
    rate = annual_rate / 100
    n = compound_frequency
    return principal * ((1 + rate / n) ** (n * years))


def annual_return(start_value: float, end_value: float, years: float) -> float:
    """
    Calculate annualized return over a period.

    Args:
        start_value: Initial investment value
        end_value: Final investment value
        years: Number of years over which the return was earned

    Returns:
        Annualized return percentage
    """
    if start_value <= 0:
        raise ValueError("Start value must be positive")
    return ((end_value / start_value) ** (1 / years) - 1) * 100


def cagr(initial_value: float, final_value: float, years: float) -> float:
    """
    Calculate Compound Annual Growth Rate (CAGR).

    Args:
        initial_value: Starting value
        final_value: Ending value
        years: Time period in years

    Returns:
        CAGR as percentage
    """
    return annual_return(initial_value, final_value, years)


def risk_adjusted_return(return_rate: float, volatility: float) -> float:
    """
    Calculate Sharpe ratio approximation (assuming risk-free rate of 0).

    Args:
        return_rate: Annual return as percentage
        volatility: Annual standard deviation as percentage

    Returns:
        Risk-adjusted return metric
    """
    return return_rate / volatility if volatility > 0 else 0


def diversification_benefit(
        asset_a_return: float,
        asset_b_return: float,
        correlation: float,
        weight_a: float = 0.5,
        weight_b: float = 0.5
) -> float:
    """
    Calculate portfolio return and diversification benefit.

    Args:
        asset_a_return: Return of asset A (%)
        asset_b_return: Return of asset B (%)
        correlation: Correlation between assets (-1 to 1)
        weight_a: Weight of asset A
        weight_b: Weight of asset B

    Returns:
        Tuple of (portfolio_return, portfolio_volatility)
    """
    std_a = 15  # Typical annual volatility assumption
    std_b = 18

    portfolio_return = weight_a * asset_a_return + weight_b * asset_b_return

    variance = (weight_a ** 2) * (std_a ** 2) + (weight_b ** 2) * (std_b ** 2) + \
               2 * weight_a * weight_b * std_a * std_b * correlation

    portfolio_volatility = math.sqrt(variance)

    return portfolio_return, portfolio_volatility


def drawdown(start_value: float, peak_value: float, current_value: float) -> float:
    """
    Calculate maximum drawdown.

    Args:
        start_value: Initial investment
        peak_value: Highest value reached
        current_value: Current value

    Returns:
        Maximum drawdown as percentage
    """
    if peak_value <= 0:
        return 0
    return (1 - min(peak_value, current_value) / peak_value) * 100


def required_investment(
        target_return: float,
        annual_return_rate: float,
        years: float,
        compound_frequency: int = 12
) -> float:
    """
    Calculate required monthly investment to reach a target amount.

    Args:
        target_return: Target amount to reach
        annual_return_rate: Expected annual return (%)
        years: Investment period
        compound_frequency: Compounding frequency

    Returns:
        Required monthly investment
    """
    r = annual_return_rate / 100 / compound_frequency
    n = compound_frequency * years
    if r == 0:
        return target_return / n
    return (target_return / (r * (n - r * (n - 1))) - 1) * compound_frequency


def inflation_adjusted_value(future_value: float, inflation_rate: float, years: float) -> float:
    """
    Calculate inflation-adjusted value of a future amount.

    Args:
        future_value: Future value in today's dollars
        inflation_rate: Annual inflation rate (%)
        years: Number of years from now

    Returns:
        Value in today's dollars
    """
    rate = inflation_rate / 100
    return future_value / ((1 + rate) ** years)


class InvestmentPlan:
    """
    Plan and track investment goals.
    """

    def __init__(self, name: str, target_amount: float, years: float,
                 monthly_contribution: float = 0, expected_return: float = 7):
        self.name = name
        self.target_amount = target_amount
        self.years = years
        self.monthly_contribution = monthly_contribution
        self.expected_return = expected_return

    def calculate_projection(self) -> Dict:
        """Calculate investment projection."""
        r = self.expected_return / 100 / 12
        n = 12 * self.years

        # Future value with regular contributions
        if r > 0:
            fv = self.monthly_contribution * ((1 + r) ** n - 1) / r
        else:
            fv = self.monthly_contribution * n

        # Add initial investment growth (if any)
        initial_growth = 0

        total_contributions = self.monthly_contribution * n

        return {
            'name': self.name,
            'target': self.target_amount,
            'years': self.years,
            'monthly_contribution': self.monthly_contribution,
            'total_contributions': total_contributions,
            'projected_value': round(fv + initial_growth, 2),
            'total_return': round((fv + initial_growth - total_contributions) / total_contributions * 100, 2) if total_contributions > 0 else 0,
            'on_track': (fv + initial_growth) >= self.target_amount
        }

    def adjust_contribution(self, months: int) -> float:
        """
        Calculate new monthly contribution to stay on track.

        Args:
            months: Number of months until adjustment

        Returns:
            Required new monthly contribution
        """
        r = self.expected_return / 100 / 12
        n_remaining = 12 * (self.years - months / 12)
        if r > 0:
            return (self.target_amount / ((1 + r) ** n_remaining - 1) * r) * 12
        return self.target_amount / n_remaining


def financial_summary(*plans: InvestmentPlan) -> Dict:
    """
    Generate summary of all investment plans.

    Args:
        *plans: InvestmentPlan instances

    Returns:
        Dictionary with summary statistics
    """
    total_target = sum(p.target_amount for p in plans)
    total_monthly = sum(p.monthly_contribution for p in plans)
    total_years = max(p.years for p in plans)

    projections = [p.calculate_projection() for p in plans]

    avg_return = sum(p.expected_return for p in plans) / len(plans) if plans else 0

    return {
        'total_target': total_target,
        'total_monthly_contribution': total_monthly,
        'total_years': total_years,
        'average_expected_return': round(avg_return, 2),
        'plans': projections,
        'summary': {
            'total_target': total_target,
            'total_monthly': total_monthly,
            'on_track_count': sum(1 for p in projections if p['on_track']),
            'off_track_count': len(projections) - sum(1 for p in projections if p['on_track'])
        }
    }
