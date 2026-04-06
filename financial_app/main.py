#!/usr/bin/env python3
"""
Financial App - Main Entry Point
A simple Python financial application demonstrating investment calculations,
portfolio management, and transaction logging.
"""

import sys
from typing import Optional

from .calculator import (
    compound_interest,
    annual_return,
    cagr,
    required_investment,
    InvestmentPlan,
    financial_summary
)

from .portfolio import (
    Portfolio,
    Position,
    monte_carlo_simulation,
    PortfolioAnalyzer,
    TransactionLogger
)


def print_header():
    """Print application header."""
    print("=" * 60)
    print("       FINANCIAL APP - Investment Calculator")
    print("=" * 60)
    print()


def compound_interest_example() -> None:
    """Example: Calculate compound interest."""
    print_header()
    print("📊 COMPOUND INTEREST CALCULATOR")
    print("-" * 40)

    examples = [
        {
            'principal': 10000,
            'rate': 7,
            'years': 10,
            'description': 'Standard investment'
        },
        {
            'principal': 5000,
            'rate': 10,
            'years': 15,
            'description': 'Aggressive growth'
        },
        {
            'principal': 20000,
            'rate': 5,
            'years': 20,
            'description': 'Conservative investment'
        }
    ]

    for ex in examples:
        result = compound_interest(
            ex['principal'],
            ex['rate'],
            ex['years'],
            compound_frequency=12
        )
        gain = result - ex['principal']
        print(f"\n{ex['description']}:")
        print(f"  Initial: €{ex['principal']:,.2f}")
        print(f"  Rate: {ex['rate']}% annual, compounded monthly")
        print(f"  Duration: {ex['years']} years")
        print(f"  Final Value: €{result:,.2f}")
        print(f"  Total Gain: €{gain:,.2f} ({gain/ex['principal']*100:.1f}%)")

    print("\n" + "-" * 40)
    print("Tip: Higher rates and longer periods lead to greater gains!")


def annual_return_example() -> None:
    """Example: Calculate annualized returns."""
    print_header()
    print("📈 ANNUALIZED RETURN CALCULATOR")
    print("-" * 40)

    # Scenario: Investment grew from €10,000 to €15,000 over 5 years
    start = 10000
    end = 15000
    years = 5

    annual_return = annual_return(start, end, years)
    cagr = cagr(start, end, years)

    print(f"\nInvestment Performance:")
    print(f"  Starting Value: €{start:,.2f}")
    print(f"  Ending Value: €{end:,.2f}")
    print(f"  Period: {years} years")
    print(f"  Total Gain: €{end - start:,.2f}")
    print(f"  Total Return: {(end/start - 1) * 100:.1f}%")
    print(f"  Annualized Return: {annual_return:.2f}%")
    print(f"  CAGR: {cagr:.2f}%")


def investment_planning() -> None:
    """Example: Investment planning and goals."""
    print_header()
    print("🎯 INVESTMENT PLANNING")
    print("-" * 40)

    # Define investment goals
    plans = [
        InvestmentPlan(
            name="Retirement Fund",
            target_amount=500000,
            years=25,
            monthly_contribution=500,
            expected_return=8
        ),
        InvestmentPlan(
            name="Emergency Fund",
            target_amount=50000,
            years=5,
            monthly_contribution=300,
            expected_return=7
        ),
        InvestmentPlan(
            name="Down Payment",
            target_amount=100000,
            years=10,
            monthly_contribution=1000,
            expected_return=6
        )
    ]

    summary = financial_summary(*plans)

    print(f"\nInvestment Goals Summary:")
    print(f"  Total Target: €{summary['total_target']:,.2f}")
    print(f"  Total Monthly Contribution: €{summary['total_monthly_contribution']:,.2f}")
    print(f"  Average Expected Return: {summary['average_expected_return']}%")
    print()

    for plan_summary in summary['plans']:
        status = "✅ On Track" if plan_summary['on_track'] else "⚠️ Off Track"
        print(f"\n{plan_summary['name']}:")
        print(f"  Target: €{plan_summary['target']:,.2f}")
        print(f"  Monthly: €{plan_summary['monthly_contribution']:,.2f}")
        print(f"  Duration: {plan_summary['years']} years")
        print(f"  Projected Value: €{plan_summary['projected_value']:,.2f}")
        print(f"  Status: {status}")

    print(f"\n{'-' * 40}")
    print(f"Summary: {summary['summary']['on_track_count']}/{len(summary['plans'])} goals on track")


def required_investment_calculator() -> None:
    """Example: Calculate required investment to reach target."""
    print_header()
    print("💰 REQUIRED INVESTMENT CALCULATOR")
    print("-" * 40)

    target = 100000  # €100,000 target
    rates = [5, 7, 9, 12]
    years = 20

    print(f"\nTarget: €{target:,}")
    print(f"Period: {years} years")
    print(f"{'Annual Return':<15} {'Monthly Needed':<15}")
    print("-" * 40)

    for rate in rates:
        monthly = required_investment(target, rate, years, 12)
        print(f"{rate:>3}%              €{monthly:>11,.2f}")

    print(f"\n{'-' * 40}")
    print("Higher expected returns mean lower monthly contributions needed!")


def monte_carlo_demo() -> None:
    """Example: Monte Carlo simulation for investment projection."""
    print_header()
    print("🎲 MONTE CARLO INVESTMENT SIMULATION")
    print("-" * 40)

    simulation = monte_carlo_simulation(
        initial_capital=10000,
        expected_return=8,
        volatility=15,
        num_simulations=1000,
        time_horizon_years=10
    )

    print(f"\nSimulation Results:")
    print(f"  Initial Capital: €{simulation['initial_capital']:,.2f}")
    print(f"  Expected Return: {simulation['expected_return']}%")
    print(f"  Volatility: {simulation['volatility']}%")
    print(f"  Horizon: {simulation['time_horizon_years']} years")
    print()
    print(f"  📊 Results:")
    print(f"    Mean Final Value: €{simulation['mean_final_value']:,.2f}")
    print(f"    Median Final Value: €{simulation['median_final_value']:,.2f}")
    print(f"    Min Final Value: €{simulation['min_final_value']:,.2f}")
    print(f"    Max Final Value: €{simulation['max_final_value']:,.2f}")
    print(f"    Probability of Loss: {simulation['probability_of_loss']}%")


def portfolio_demo() -> None:
    """Example: Portfolio management demonstration."""
    print_header()
    print("📁 PORTFOLIO MANAGEMENT DEMO")
    print("-" * 40)

    # Create a portfolio
    portfolio = Portfolio(name="Demo Portfolio")

    # Add initial positions
    portfolio.add_position("AAPL", 100, 175.50)
    portfolio.add_position("GOOGL", 20, 140.25)
    portfolio.add_position("MSFT", 50, 380.00)
    portfolio.add_position("BTC", 0.25, 45000.00)

    # Simulate price updates
    price_updates = {
        "AAPL": 182.50,
        "GOOGL": 148.75,
        "MSFT": 395.25,
        "BTC": 46500.00
    }
    portfolio.update_all_prices(price_updates)

    print(f"\nPortfolio: {portfolio.name}")
    print(f"  Total Value: €{portfolio.total_market_value:,.2f}")
    print(f"  Total Return: {portfolio.total_return_pct:.2f}%")

    print(f"\n  Positions:")
    for symbol, pos in portfolio.positions.items():
        print(f"    {symbol}:")
        print(f"      Quantity: {pos.quantity}")
        print(f"      Avg Cost: €{pos.average_cost:.2f}")
        print(f"      Current Price: €{pos.current_price:.2f}")
        print(f"      Market Value: €{pos.market_value:,.2f}")
        print(f"      Gain/Loss: €{pos.gain_loss:,.2f} ({pos.gain_loss_pct:.1f}%)")

    # Show asset allocation
    analyzer = PortfolioAnalyzer(portfolio)
    allocation = analyzer.asset_allocation()
    print(f"\n  Asset Allocation:")
    for symbol, weight in allocation.items():
        print(f"    {symbol}: {weight:.1f}%")

    print(f"\n{'-' * 40}")
    print("For full interactive use, use the CLI interface below.")


def interactive_mode() -> None:
    """Run interactive financial calculator."""
    print_header()
    print("🖥️  INTERACTIVE MODE")
    print("-" * 40)
    print("Select an operation:")
    print("  1. Compound Interest Calculator")
    print("  2. Annual Return Calculator")
    print("  3. Investment Planning")
    print("  4. Required Investment Calculator")
    print("  5. Monte Carlo Simulation")
    print("  6. Portfolio Demo")
    print("  7. Exit")
    print()

    while True:
        try:
            choice = input("Enter choice (1-7): ").strip()

            if choice == "1":
                compound_interest_example()
            elif choice == "2":
                annual_return_example()
            elif choice == "3":
                investment_planning()
            elif choice == "4":
                required_investment_calculator()
            elif choice == "5":
                monte_carlo_demo()
            elif choice == "6":
                portfolio_demo()
            elif choice == "7":
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please enter 1-7.")
        except EOFError:
            print("\nGoodbye!")
            break
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Financial App - Investment Calculator & Portfolio Manager"
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run interactive mode"
    )
    parser.add_argument(
        "--demo", "-d",
        choices=["interest", "return", "planning", "investment", "monte-carlo", "portfolio"],
        help="Run a specific demo"
    )

    args = parser.parse_args()

    print_header()
    print("Financial App v0.1.0")
    print()

    if args.interactive:
        interactive_mode()
    elif args.demo:
        if args.demo == "interest":
            compound_interest_example()
        elif args.demo == "return":
            annual_return_example()
        elif args.demo == "planning":
            investment_planning()
        elif args.demo == "investment":
            required_investment_calculator()
        elif args.demo == "monte-carlo":
            monte_carlo_demo()
        elif args.demo == "portfolio":
            portfolio_demo()
    else:
        # Run all demos by default
        compound_interest_example()
        print("\n" + "=".ljust(60))
        annual_return_example()
        print("\n" + "=".ljust(60))
        investment_planning()
        print("\n" + "=".ljust(60))
        required_investment_calculator()
        print("\n" + "=".ljust(60))
        monte_carlo_demo()
        print("\n" + "=".ljust(60))
        portfolio_demo()

        print("\n" + "=".ljust(60))
        print("📚 DOCS & EXAMPLES")
        print("-" * 40)
        print()
        print("Available modules:")
        print("  - calculator.py  : Investment calculations")
        print("  - portfolio.py   : Portfolio management")
        print()
        print("Run interactive mode:")
        print("  python financial_app/main.py --interactive")
        print()
        print("Run specific demo:")
        print("  python financial_app/main.py --demo interest")
        print("-" * 40)


if __name__ == "__main__":
    main()
