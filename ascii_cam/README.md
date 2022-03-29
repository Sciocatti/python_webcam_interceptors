# ASCII Cam

This is an webcam interceptor that captures a video feed, converts it to characters, and broadcast the converted feed out to the world.

## Getting started
> Never copy as-is, read the comments to see what happens
```bash
# Navigate to folder
cd ascii_cam
# Create virtual environment
python3 -m venv ascii_cam_venv
# Enter venv -> Ubuntu
source ascii_cam_venv/bin/activate
# Enter venv -> Windows
.\ascii_cam_venv\Scripts\activate
# Install dependencies
pip install -r requirements.txt
# Leave venv
deactivate
# Run script -> Windows
ascii_cam_venv\Scripts\python.exe main.py
```