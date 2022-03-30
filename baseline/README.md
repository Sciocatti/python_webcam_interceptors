# Baseline

This is the baseline for the other interceptors in this repo, ie what they are based on. Read each readme,
but the general shape and general `Getting Started` steps will be roughly the same.

## Getting started
> Never copy as-is, read the comments to see what happens
```bash
# Navigate to folder
cd baseline
# Create virtual environment
python3 -m venv baseline_venv
# Enter venv -> Ubuntu
source baseline_venv/bin/activate
# Enter venv -> Windows
.\baseline_venv\Scripts\activate
# Install dependencies
pip install -r requirements.txt
# Leave venv
deactivate
# Run script -> Windows
baseline_venv\Scripts\python.exe main.py