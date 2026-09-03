# GitHub Terminal Commands

Run these commands only from this project directory.

```bash
cd ~/Downloads/BloomWatch_GitHub_RUN/AlgalBloomEarlyWarningSystem_Local

# Safety check: confirm you are inside the project
pwd
ls -la

# Validate before Git
python validate_project.py
python -m pytest -q

# Initialize repository
git init
git branch -M main
git add -A
git status
git commit -m "feat: add BloomWatch algal bloom early-warning system"

git remote remove origin 2>/dev/null || true
git remote add origin https://github.com/shaunakmirajgaonkar/algal-bloom-early-warning-system.git
git remote -v
git push -u origin main
```

Never run `git add -A` from `~` or from `~/Downloads`; use the project directory above.
