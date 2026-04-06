"""
Portfolio Management Module
Provides functionality for tracking, analyzing, and rebalancing investment portfolios.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from math import sqrt


@dataclass
class Position:
    """Represents a single position in a portfolio."""
    symbol: str
    quantity: float
    average_cost: float
    purchase_date: str
    current_price: float

    @property
    def market_value(self) -> float:
        return self.quantity * self.current_price

    @property
    def cost_basis(self) -> float:
        return self.quantity * self.average_cost

    @property
    def gain_loss(self) -> float:
        return self.market_value - self.cost_basis

    @property
    def gain_loss_pct(self) -> float:
        return (self.gain_loss / self.cost_basis) * 100 if self.cost_basis > 0 else 0

    def update_price(self, new_price: float) -> None:
        self.current_price = new_price

    def to_dict(self) -> Dict:
        return {
            'symbol': self.symbol,
            'quantity': self.quantity,
            'average_cost': round(self.average_cost, 2),
            'purchase_date': self.purchase_date,
            'current_price': round(self.current_price, 2),
            'market_value': round(self.market_value, 2),
            'gain_loss': round(self.gain_loss, 2),
            'gain_loss_pct': round(self.gain_loss_pct, 2)
        }


@dataclass
class Portfolio:
    """Represents an investment portfolio."""

    name: str
    positions: Dict[str, Position] = field(default_factory=dict)
    cash_balance: float = 0.0
    created_date: str = field(default_factory=lambda: datetime.now().strftime('%Y-%m-%d'))

    @property
    def total_market_value(self) -> float:
        return sum(pos.market_value for pos in self.positions.values()) + self.cash_balance

    @property
    def total_cost_basis(self) -> float:
        return sum(pos.cost_basis for pos in self.positions.values())

    @property
    def total_gain_loss(self) -> float:
        return self.total_market_value - self.total_cost_basis

    @property
    def total_return_pct(self) -> float:
        return (self.total_gain_loss / self.total_cost_basis) * 100 if self.total_cost_basis > 0 else 0

    def add_position(self, symbol: str, quantity: float, average_cost: float,
                     purchase_date: Optional[str] = None) -> Position:
        """Add or update a position in the portfolio."""
        if purchase_date is None:
            purchase_date = datetime.now().strftime('%Y-%m-%d')
        if symbol in self.positions:
            existing = self.positions[symbol]
            combined_qty = existing.quantity + quantity
            combined_cost = (existing.quantity * existing.average_cost +
                          quantity * average_cost) / combined_qty
            existing.quantity = combined_qty
            existing.average_cost = combined_cost
        else:
            self.positions[symbol] = Position(
                symbol=symbol,
                quantity=quantity,
                average_cost=average_cost,
                purchase_date=purchase_date,
                current_price=average_cost
            )
        return self.positions[symbol]

    def remove_position(self, symbol: str) -> None:
        """Remove a position from the portfolio."""
        if symbol in self.positions:
            del self.positions[symbol]

    def update_all_prices(self, prices: Dict[str, float]) -> None:
        """Update current prices for all positions."""
        for symbol, price in prices.items():
            if symbol in self.positions:
                self.positions[symbol].update_price(price)

    def buy(self, symbol: str, quantity: float, price: float,
            commission: float = 0.0) -> None:
        """Record a purchase."""
        self.cash_balance -= (quantity * price + commission)
        self.add_position(symbol, quantity, price)

    def sell(self, symbol: str, quantity: float, price: float,
             commission: float = 0.0) -> None:
        """Record a sale."""
        pos = self.positions.get(symbol)
        if pos and quantity <= pos.quantity:
            self.cash_balance += (quantity * price - commission)
            pos.quantity -= quantity
            if pos.quantity <= 0:
                del self.positions[symbol]

    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'total_value': round(self.total_market_value, 2),
            'positions': {k: v.to_dict() for k, v in self.positions.items()},
            'cash_balance': round(self.cash_balance, 2),
            'total_return': round(self.total_return_pct, 2)
        }

    def clone(self) -> 'Portfolio':
        return Portfolio(
            name=self.name,
            positions={k: Position(
                symbol=v.symbol,
                quantity=v.quantity,
                average_cost=v.average_cost,
                purchase_date=v.purchase_date,
                current_price=v.current_price
            ) for k, v in self.positions.items()},
            cash_balance=self.cash_balance,
            created_date=self.created_date
        )


def historical_returns(prices: List[float], periods: int = 252) -> List[float]:
    """
    Calculate daily returns from price series.

    Args:
        prices: List of daily prices
        periods: Number of periods for lookback

    Returns:
        List of daily returns as percentages
    """
    if len(prices) < 2:
        return []
    returns = []
    for i in range(1, len(prices)):
        if prices[i - 1] != 0:
            returns.append(((prices[i] - prices[i - 1]) / prices[i - 1]) * 100)
    return returns


def annualized_volatility(returns: List[float], periods_per_year: float = 252) -> float:
    """
    Calculate annualized volatility (standard deviation of returns).

    Args:
        returns: List of returns (as percentages)
        periods_per_year: Trading days per year

    Returns:
        Annualized volatility as percentage
    """
    if len(returns) < 2:
        return 0.0
    mean_return = sum(returns) / len(returns)
    variance = sum((r - mean_return) ** 2 for r in returns) / (len(returns) - 1)
    return sqrt(variance) * sqrt(periods_per_year)


def monte_carlo_simulation(
        initial_capital: float,
        expected_return: float,
        volatility: float,
        num_simulations: int = 1000,
        time_horizon_years: float = 10
) -> Dict:
    """
    Run Monte Carlo simulation for investment projection.

    Args:
        initial_capital: Starting investment
        expected_return: Expected annual return (%)
        volatility: Annual volatility (%)
        num_simulations: Number of simulation paths
        time_horizon_years: Investment horizon

    Returns:
        Dictionary with results and statistics
    """
    import random
    import numpy as np

    dt = 1.0 / 252.0  # Daily time step
    mu = (expected_return / 100 - (volatility / 100) ** 2 / 2) * dt
    sigma = (volatility / 100) * sqrt(dt)

    paths = []
    for _ in range(num_simulations):
        price = initial_capital
        daily_return = np.random.normal(mu, sigma)
        price *= (1 + daily_return / 100)
        paths.append(price)

    final_values = [p[-1] for p in paths]
    geometric_mean = initial_capital * np.exp(np.mean(np.log(final_values / initial_capital)))

    return {
        'initial_capital': initial_capital,
        'num_simulations': num_simulations,
        'mean_final_value': round(np.mean(final_values), 2),
        'median_final_value': round(np.median(final_values), 2),
        'min_final_value': round(min(final_values), 2),
        'max_final_value': round(max(final_values), 2),
        'geometric_mean': round(geometric_mean, 2),
        'probability_of_loss': round(np.sum(final_values < initial_capital) / num_simulations * 100, 2)
    }


class PortfolioAnalyzer:
    """Analyze portfolio performance and risk metrics."""

    def __init__(self, portfolio: Portfolio):
        self.portfolio = portfolio

    def performance_metrics(self) -> Dict:
        """Calculate key performance metrics."""
        returns = historical_returns(self.portfolio.positions.keys())
        volatility = annualized_volatility(returns) if returns else 0.0
        sharpe_ratio = (self.portfolio.total_return_pct / 5) / volatility if volatility > 0 else 0

        return {
            'total_return': round(self.portfolio.total_return_pct, 2),
            'total_gain_loss': round(self.portfolio.total_gain_loss, 2),
            'volatility_1y': round(volatility, 2),
            'sharpe_ratio': round(sharpe_ratio, 2),
            'concentration': self.concentration_risk(),
            'largest_position': self.largest_position()
        }

    def concentration_risk(self) -> float:
        """Calculate portfolio concentration (Herfindahl-Hirschman Index)."""
        if not self.portfolio.positions:
            return 0.0
        weights = [pos.market_value / self.portfolio.total_market_value
                   for pos in self.portfolio.positions.values()]
        return sum(w ** 2 for w in weights) * 100

    def largest_position(self) -> Dict:
        """Get information about the largest position."""
        if not self.portfolio.positions:
            return {'symbol': None, 'weight': 0.0}
        largest = max(self.portfolio.positions.values(),
                     key=lambda p: p.market_value)
        weight = largest.market_value / self.portfolio.total_market_value
        return {
            'symbol': largest.symbol,
            'market_value': round(largest.market_value, 2),
            'weight': round(weight * 100, 2)
        }

    def asset_allocation(self) -> Dict:
        """Get asset allocation breakdown."""
        allocation = {}
        total = self.portfolio.total_market_value
        for pos in self.portfolio.positions.values():
            weight = (pos.market_value / total) * 100 if total > 0 else 0
            allocation[pos.symbol] = round(weight, 2)
        allocation['cash'] = round((self.portfolio.cash_balance / total) * 100, 2) if total > 0 else 0
        return allocation

    def rebalancing_needed(self, tolerance: float = 5.0) -> Dict:
        """
        Check if portfolio needs rebalancing.

        Args:
            tolerance: Maximum deviation from target weights (%)

        Returns:
            Dictionary with rebalancing recommendations
        """
        if not self.portfolio.positions:
            return {'needs_rebalancing': False, 'reason': 'No positions'}

        target_weights = {k: 1.0 / len(self.portfolio.positions) for k in self.portfolio.positions}
        current_weights = {
            symbol: (pos.market_value / self.portfolio.total_market_value) * 100
            for symbol, pos in self.portfolio.positions.items()
        }
        total_value = self.portfolio.total_market_value
        needs_rebalancing = False
        changes = []

        for symbol, target_weight in target_weights.items():
            current_weight = current_weights.get(symbol, 0)
            deviation = abs(current_weight - target_weight * 100)
            if deviation > tolerance:
                needs_rebalancing = True
                adjustment = total_value * (target_weight * 100 - current_weight) / 100
                changes.append({
                    'symbol': symbol,
                    'current_weight': round(current_weight, 2),
                    'target_weight': round(target_weight * 100, 2),
                    'deviation': round(deviation, 2),
                    'adjustment': round(adjustment, 2)
                })

        return {
            'needs_rebalancing': needs_rebalancing,
            'tolerance': tolerance,
            'changes': changes
        }


class TransactionLogger:
    """Log and track all portfolio transactions."""

    def __init__(self):
        self.transactions: List[Dict] = []

    def log(self, transaction_type: str, symbol: str, quantity: float,
            price: float, date: Optional[str] = None, commission: float = 0.0) -> None:
        """Record a transaction."""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        self.transactions.append({
            'id': len(self.transactions) + 1,
            'date': date,
            'type': transaction_type,
            'symbol': symbol,
            'quantity': quantity,
            'price': round(price, 2),
            'total_value': round(quantity * price, 2),
            'commission': round(commission, 2)
        })

    def get_summary(self, symbol: Optional[str] = None) -> Dict:
        """Get transaction summary."""
        if symbol:
            trans = [t for t in self.transactions if t['symbol'] == symbol]
        else:
            trans = self.transactions

        if not trans:
            return {'summary': 'No transactions found'}

        purchases = [t for t in trans if t['type'] == 'BUY']
        sales = [t for t in trans if t['type'] == 'SELL']

        total_purchased = sum(p['total_value'] + p.get('commission', 0) for p in purchases)
        total_sold = sum(s['total_value'] - s.get('commission', 0) for s in sales)

        return {
            'symbol': symbol,
            'total_transactions': len(trans),
            'purchases': len(purchases),
            'sales': len(sales),
            'total_purchased': round(total_purchased, 2),
            'total_sold': round(total_sold, 2)
        }

    def export_to_json(self, filename: str) -> None:
        """Export transactions to JSON file."""
        with open(filename, 'w') as f:
            json.dump(self.transactions, f, indent=2)

    def import_from_json(self, filename: str) -> None:
        """Import transactions from JSON file."""
        with open(filename, 'r') as f:
            self.transactions = json.load(f)
