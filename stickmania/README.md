# Stickmania

This is (going to be) an webcam interceptor that captures a video feed, processes and draws media pipe model outputs onto the feed, and broadcast the modified feed out to the world.

## Getting started
> Never copy as-is, read the comments to see what happens
```bash
# Navigate to folder
cd stickmania
# Create virtual environment
python3 -m venv stickmania_venv
# Enter venv -> Ubuntu
source stickmania_venv/bin/activate
# Enter venv -> Windows
.\stickmania_venv\Scripts\activate
# Install dependencies
pip install -r requirements.txt
# Leave venv
deactivate
# Run script -> Windows
stickmania_venv\Scripts\python.exe main.py
```