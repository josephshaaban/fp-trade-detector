# FundingPips Trade Detector

## Project Structure

```
fp-trade-detector/
├── config/
│   └── default.yaml
├── core/
│   ├── __init__.py
│   └── config.py
├── data/
│   ├── seeds.py               # Generate/mock trades data
│   └── trades.csv             # Generated trades data
├── trades/
│   ├── __init__.py
│   ├── loader.py              # Load + preprocess CSV/JSON/DB
│   ├── matcher.py             # Matching logic
│   ├── config.py              # Load config (Mode A / Mode B)
│   ├── report.py              # Output generation
│   └── models.py              # Data models with pydantic
├── tests/
│   └── test_matcher.py
├── main.py
├── requirements.txt
├── setup_and_run.ps1          # One-click setup and run for PowerShell
├── setup_and_run.bat          # One-click setup and run for Batch
└── README.md
```

---

## Setup and Installation

### Prerequisites
- Python 3.8 or higher
- `pip` (Python package manager)
- A virtual environment (optional but recommended)

### Installation Steps
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
- **One-Click Setup and Run:** Simplifies the developer experience with pre-configured scripts.
- **Trade Matching:** Supports multiple matching strategies (Mode A and Mode B).
- **Filters:** Includes customizable filters for trade duration and lot size.
- **Extensible Design:** Modular architecture for easy addition of new features.

---

Let me know if you need further updates or clarifications!
