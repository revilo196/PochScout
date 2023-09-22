# PochScout

    ⚠️ WARNING
    This is for educational Purposes only. Authors of this Repo or associated repos take no responsibility for its usage.

## Overview
This Python script automates exploration of Pochven space in the game "EVE Online." It captures game data, navigates star systems, and reports information to a central server.

## Features
- Screenshots with OCR.
- Overview navigation.
- Centralized reporting.
- Configurable settings.
- Modular structure.

## Getting Started and Configuration
1. Install Python (3.7+).
2. Install required packages: `pip install -r requirements.txt`.
3. **Setup and Configuration:**
     - Configure the server data endpoint and API key by adjusting the following files:
       - `destination.txt`: Contains the server's data endpoint URL.
       - `key.txt`: Contains the API key for reporting.
     - Adjust the following settings in your "EVE Online" client:
       - Set the UI-Scale to 125%.
       - Set Text-size to Large.
       - Disable transparency
     - Configure the game client as follows:
       - Set up the overview with gates only.
       - Configure DScan settings for ships only.
       - Configure the Probe scanner for anomalies.
     - Enable "Potato mode" by pressing Ctrl+Shift+F9.
     - Calibrate screen regions using the "setup_capture.py" script.
4. Undock your ship and start this script:  `python main.py`.

## Usage
- Run the script alongside EVE Online.
- It continuously explores Pochven space and reports data.
- Review documentation for details.
