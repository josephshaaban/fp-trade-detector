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
│   ├── seeds.py               # Genereate/mock trades data
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
└── README.md
```
