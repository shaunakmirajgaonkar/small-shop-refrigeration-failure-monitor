# Run Instructions

```bash
cd ~/Downloads
rm -rf BloomWatch_GitHub_RUN
mkdir -p BloomWatch_GitHub_RUN
unzip -q "AlgalBloomEarlyWarningSystem_GitHub_Complete.zip" -d BloomWatch_GitHub_RUN
cd BloomWatch_GitHub_RUN/AlgalBloomEarlyWarningSystem_Local
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m py_compile app.py bloom_engine.py validate_project.py run.py
python validate_project.py
python -m pytest -q
python run.py
```

`run.py` searches for a free port from 8501 through 8599.

Run tests from the project directory only.
