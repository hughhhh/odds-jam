# Odds Pulling Script

This Python script is designed to pull odds from a specified source. It can be run as a one-time pull or continuously with a polling mechanism.

## Prerequisites

Before you begin, ensure you have Python installed on your system. Python 3.6 or higher is recommended. You can download Python from [python.org](https://www.python.org/downloads/).

## Installation

Follow these steps to set up the script environment and install necessary dependencies:

1. **Clone the repository** (if applicable):
   ```bash
   git clone https://github.com/hughhhh/odds-jam.git
   cd odds-jam

2. **Create a Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

# Usage
To use the script, you can perform a one-time pull of the odds or run it in a polling mode which continuously checks and updates the odds.
```
# One time pull
python pull_odds.py draftkings

# Continuous polling every 5 seconds
python pull_odds.py draftkings --poll
```

### Stopping the Script
To stop the script when it's running in polling mode, you can simply press CTRL+C in your terminal. This will terminate the script.