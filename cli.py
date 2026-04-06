#!/usr/bin/env python3
"""
Financial App CLI - Command Line Interface
"""

import sys
import argparse
from financial_app.main import main, compound_interest_example, annual_return_example, \
    investment_planning, required_investment_calculator, monte_carlo_demo, portfolio_demo


def create_cli_parser() -> argparse.ArgumentParser:
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(
        prog="financial_app",
        description="Financial App CLI - Investment Calculator & Portfolio Manager"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Compound interest
    interest_parser = subparsers.add_parser("interest", help="Calculate compound interest")
    interest_parser.add_argument("--principal", type=float, default=10000)
    interest_parser.add_argument("--rate", type=float, default=7)
    interest_parser.add_argument("--years", type=float, default=10)

    # Annual return
    return_parser = subparsers.add_parser("return", help="Calculate annualized returns")
    return_parser.add_argument("--start", type=float, default=10000)
    return_parser.add_argument("--end", type=float, default=15000)
    return_parser.add_argument("--years", type=float, default=5)

    # Investment planning
    planning_parser = subparsers.add_parser("planning", help="Investment planning")
    planning_parser.add_argument("--target", type=float, default=500000)
    planning_parser.add_argument("--years", type=float, default=25)
    planning_parser.add_argument("--monthly", type=float, default=500)
    planning_parser.add_argument("--return", type=float, default=8)

    # Required investment
    investment_parser = subparsers.add_parser("investment", help="Required investment calculator")
    investment_parser.add_argument("--target", type=float, default=100000)
    investment_parser.add_argument("--years", type=float, default=20)

    # Monte Carlo
    mc_parser = subparsers.add_parser("monte-carlo", help="Monte Carlo simulation")
    mc_parser.add_argument("--capital", type=float, default=10000)
    mc_parser.add_argument("--return", type=float, default=8)
    mc_parser.add_argument("--volatility", type=float, default=15)

    # Portfolio
    portfolio_parser = subparsers.add_parser("portfolio", help="Portfolio demo")

    return parser


def run_cli():
    """Run the CLI."""
    parser = create_cli_parser()
    args = parser.parse_args()

    if args.command is None:
        main()
    else:
        # Run specific command
        if args.command == "interest":
            compound_interest_example()
        elif args.command == "return":
            annual_return_example()
        elif args.command == "planning":
            investment_planning()
        elif args.command == "investment":
            required_investment_calculator()
        elif args.command == "monte-carlo":
            monte_carlo_demo()
        elif args.command == "portfolio":
            portfolio_demo()


if __name__ == "__main__":
    run_cli()
