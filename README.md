# Algal Bloom Early-Warning System — BloomWatch Local

A privacy-conscious, local-first dashboard for screening potential harmful algal-bloom risk in lakes and reservoirs using water temperature, nutrients, rainfall, flow, chlorophyll-a, turbidity, and locally supplied satellite-observation metadata.

## Highlights
- Explainable 0–100 bloom-risk scoring
- Low / Moderate / High / Critical risk bands
- Advanced Command Center
- Risk Landscape
- Waterbody Deep Dive
- Drivers Matrix
- Satellite Intelligence
- Hydrology Trends
- Scenario Lab
- Data Quality Lab
- Reports and CSV export
- Automatic local port selection (8501–8599)
- No external APIs, cloud AI, or remote satellite dependency

## Project structure
```text
AlgalBloomEarlyWarningSystem_Local/
├── app.py
├── bloom_engine.py
├── run.py
├── validate_project.py
├── requirements.txt
├── pytest.ini
├── data/
├── assets/
├── tests/
├── doc/
├── .env.example
├── .gitignore
├── ACKNOWLEDGMENTS.md
├── CHANGELOG.md
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── GITHUB_SETUP.md
├── GITHUB_TERMINAL_COMMANDS.md
├── LICENSE
├── PROJECT_FILE_INVENTORY.md
├── README.md
├── SECURITY.md
└── run instructions.md
```

## Run
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m py_compile app.py bloom_engine.py validate_project.py run.py
python validate_project.py
python -m pytest -q
python run.py
```

## Responsible use
The score is an early-warning screening indicator. It does not confirm toxins, species identity, public-health status, or regulatory compliance and should not replace field sampling, laboratory analysis, or qualified environmental-health decisions.
