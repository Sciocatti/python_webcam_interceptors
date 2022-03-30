# Live Translator
This is an webcam interceptor that captures a video feed as well as audio from your mic, translates the audio into a desired language, and draws it onto a new video feed, which is then sent out to the world.
 
### Dependencies
Pyaudio can sometimes break when installing on Windows. As such we dont use requirements.txt here, rather just create and enter the virtual environment
```bash
cd live_translator
python3 -m venv live_translator_venv
# On Windows
.\live_translator_venv\Scripts\activate
```
and run
```bash
pip install SpeechRecognition
pip install deep-translator
pip install opencv-python
pip install pyvirtualcam
pip install pyaudio
```
and if the pyaudio install fails on Windows also run
```bash
pip install pipwin
# Keep doing the below line until it works. If their server is congested it breaks.
pipwin install pyaudio
```
Finally, leave the virtual environment with
```bash
deactivate
```