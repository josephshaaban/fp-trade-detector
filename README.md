# FundingPips Trade Detector

## Project Structure

```
fp-trade-detector/
├── config/
│   ├── logger.yaml            # Logger configuration
│   └── default.yaml           # Configuration file for the project
├── templates
│   └── report_template.html   # Report generating template
├── core/
│   ├── __init__.py
│   └── config.py              # Configuration models & logic
├── data/
│   ├── discover_data.py       # Helping tool to understand the data
│   ├── seeds.py               # Generate/mock trades data
│   └── trades.csv             # Optional: Trades data file
│   └── accounts.csv           # Optional: Accounts data file
├── trades
│   ├── __init__.py
│   ├── loaders                # Load + preprocess CSV/JSON/DB
│   │   ├── __init__.py
│   │   ├── base_trade_loader.py
│   │   ├── csv_loader.py
│   │   ├── loader_factory.py
│   │   └── sqlite_loader.py
│   ├── models.py
│   ├── reoport.py             # Output generation
│   └── risk_engine
│       ├── categorize.py      # Categorize Copy, reverse, partial copy
│       ├── filters.py         # Plugable filters (used for bonus points)
│       └── matcher            # Matching logic
│           ├── __init__.py
│           ├── base_matcher.py
│           ├── mode_a_matcher.py
│           └── mode_b_matcher.py        
├── tests/
│   └── test_matcher.py        # Unit tests for matching logic
├── helpers.py
├── main.py                    # Entry point for the project
├── requirements.txt           # Python dependencies
├── setup_and_run.ps1          # One-click setup and run for PowerShell
├── setup_and_run.bat          # One-click setup and run for Batch
└── README.md                  # Project documentation
```

---

## Setup and Configuration

### Prerequisites
- Python 3.8 or higher
- `pip` (Python package manager)
- A virtual environment (optional but recommended)

### Configuration
Before running the project, ensure it is properly configured:
1. **Edit the `default.yaml` file in the `config/` folder:**
   - This file contains all the necessary configuration options for the project, such as mode selection, data source paths, and output directories.
   - Example:
     ```yaml
     mode: "A"
     data_source: "csv"
     output_dir: "reports"
     dt_window: 300

     data_sources:
      trades:
        type: csv   # or sqlite
        path: ./data/test_task_trades_short.csv
        parse_dates: ["opened_at", "closed_at"]
      accounts:
        type: csv
        path: ./data/test_task_accounts.csv
        parse_dates: []
     ```

2. **Optional: Copy Data Files to the `data/` Folder:**
   - You can copy your `trades.csv` and `accounts.csv` files to the `data/` folder if you want to use custom data for execution.

---

## Installation Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/fp-trade-detector.git
   cd fp-trade-detector
   ```

2. **One-Click Setup and Run (Developer Experience - DX):**
   - For PowerShell:
     ```powershell
     .\setup_and_run.ps1
     ```
   - For Command Prompt (Batch):
     ```cmd
     setup_and_run.bat
     ```

   These scripts will:
   - Create a virtual environment.
   - Install all dependencies from `requirements.txt`.
   - Run the `main.py` script.

3. **Manual Setup (Optional):**
   - Create and activate a virtual environment:
     ```bash
     python -m venv .venv
     source .venv/bin/activate  # On Windows: .venv\Scripts\activate
     ```
   - Install dependencies:
     ```bash
     pip install -r requirements.txt
     ```
   - Run the main script:
     ```bash
     python main.py
     ```

---

## Features
- **Configurable Modes:** Supports multiple matching strategies (Mode A and Mode B) using the Strategy design pattern.
- **Flexible Data Loading:** Dynamically loads data from various sources (CSV, JSON, database) using the Factory design pattern.
- **One-Click Setup:** Simplifies the developer experience with pre-configured scripts.
- **Extensible Design:** Modular architecture for easy addition of new features.

---

## Design Patterns Used

1. **Strategy Design Pattern:**
   - The project uses the Strategy design pattern to enable configurable mode execution (e.g., Mode A, Mode B).
   - Each mode has its own matching logic implemented as a separate strategy class.

2. **Factory Design Pattern:**
   - The Factory design pattern is used for configurable data source type loading.
   - This allows the project to support multiple data sources (e.g., CSV, JSON, database) by dynamically creating the appropriate loader.

---

