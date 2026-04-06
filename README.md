# Financial App

A simple Python financial application demonstrating investment calculations, portfolio management, and transaction logging.

## Features

- 📊 **Compound Interest Calculator** - Calculate returns with various compounding frequencies
- 📈 **Annual Return Calculator** - Calculate annualized and CAGR returns
- 🎯 **Investment Planning** - Plan and track investment goals
- 💰 **Required Investment Calculator** - Determine monthly contributions needed
- 🎲 **Monte Carlo Simulation** - Simulate investment projections
- 📁 **Portfolio Management** - Track positions, calculate allocation, monitor performance

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd financial_app
   ```

2. Install dependencies (only requires Python 3.7+):
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Command Line Interface

```bash
# Run all demonstrations
python cli.py

# Run specific calculation
python cli.py interest --rate 8 --years 10
python cli.py planning --target 500000 --monthly 300
python cli.py monte-carlo --return 8 --volatility 15
```

### Interactive Mode

```bash
python main.py --interactive
```

### As a Python Module

```python
from financial_app.calculator import compound_interest, annual_return

# Calculate compound interest
result = compound_interest(10000, 7, 10)
print(f"Final value: ${result:,.2f}")

# Calculate annualized return
return_pct = annual_return(10000, 15000, 5)
print(f"Annualized return: {return_pct:.2f}%")
```

## Project Structure

```
financial_app/
├── financial_app/
│   ├── __init__.py       # Package initialization
│   ├── calculator.py     # Investment calculations
│   ├── portfolio.py      # Portfolio management
│   └── main.py           # Main application
├── cli.py                # Command line interface
└── README.md             # This file
```

## Modules

### calculator.py
- `compound_interest()` - Compound interest with regular compounding
- `annual_return()` - Annualized return over a period
- `cagr()` - Compound Annual Growth Rate
- `risk_adjusted_return()` - Sharpe ratio approximation
- `diversification_benefit()` - Portfolio return and volatility
- `drawdown()` - Maximum drawdown calculation
- `required_investment()` - Monthly contribution for target
- `InvestmentPlan` - Plan and track investment goals
- `financial_summary()` - Summary of multiple investment plans

### portfolio.py
- `Position` - Represents a single portfolio position
- `Portfolio` - Manages multiple positions with buy/sell
- `historical_returns()` - Calculate daily returns from price series
- `annualized_volatility()` - Annualized standard deviation
- `monte_carlo_simulation()` - Investment projection simulation
- `PortfolioAnalyzer` - Performance and risk metrics
- `TransactionLogger` - Log and track transactions

## License

MIT License - feel free to use this code for your own projects.

## Contributing

This is an example project. Feel free to extend it with your own features!
