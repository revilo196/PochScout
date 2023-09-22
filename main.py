"""
EVE Online Pochven Space Exploration and Reporting Script

Description:
This Python script is designed for automating the exploration of Pochven Space within the game "EVE Online."
It continuously explores the unique Pochven region, interfaces with the game client to navigate through star systems,
and reports gathered information to a central location.

Key Features and Functionality:
- Captures screenshots and uses OCR to extract information.
- Identifies and navigates gates within the overview.
- Sends collected information to a remote central location for analysis and reporting.

Setup and Configuration:
1. Adjust the following settings in your "EVE Online" client:
   - Set the UI-Scale to 125%.
   - Set Text-size to Large.
2. Configure the game client as follows:
   - Set up the overview with gates only.
   - Configure DScan settings for ships only.
   - Configure the Probe scanner for anomalies.
3. Enable "Potato mode" by pressing Ctrl+Shift+F9.
4. Calibrate screen regions using the "setup_capture.py" script.
5. Undock your ship and start this script.

External Files and Configurations:
- The script uses external files for server data endpoint and API key information:
  - "destination.txt": Contains the server's data endpoint URL.
  - "key.txt": Contains the API key for reporting.
- The "screen_config.yaml" file specifies screen region coordinates for various game elements.

Important Notes:
- This script is specifically tailored for exploring the unique Pochven region in "EVE Online" and may not be suitable for other areas.
- The script operates in a continuous loop, exploring Pochven Space and reporting information to a central location.
- Exercise caution when using automation scripts in online games like "EVE Online" to avoid potential account issues.

"""
import sys

import pyautogui
import tesserocr
from PIL import Image
import jellyfish
import json
import requests
import random
import logging
import mss.tools
import yaml
import signal

logging.basicConfig(filename='pylot.log', encoding='utf-8', level=logging.DEBUG, format='%(asctime)s %(message)s')


# --------------------- SETUP -----------------------
# 0. use 125% UI-Scale and Text-size: Large in settings
# 1. setup Overview with gates only
# 2. setup DScan with ships only
# 3. setup Probe scaner only for Anomalies
# 4. put client in Potato mode Ctrl+Shift+F9
# 5. Calibrate screen regions using the setup_capture.py
# 6. Undock and start this script
# --------------------------------------------------


def grab_win(bbox):
    """
       Captures a screenshot of the specified region and applies an image filter.

       Args:
           bbox (tuple): A tuple representing the coordinates of the region to capture (left, top, width, height).

       Returns:
           Image: A filtered PIL Image object.
       """
    monitor = {"top": bbox[1], "left": bbox[0], "width": bbox[2], "height": bbox[3]}
    sct_img = sct.grab(monitor)
    img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX").convert("L").point(
        lambda p: p if p > threshold else 0)
    return img


def import_pochven() -> list:
    """
    Imports a list of Pochven system names from a text file.

    Returns:
        list: A list of Pochven system names.
    """
    with open("pochven.txt", "r") as f:
        return [line.strip() for line in f.readlines()]


def match_system(ocr_estimate: str) -> (str, int):
    """
    Matches an OCR-recognized string to the best-matching Pochven system name.

    Args:
        ocr_estimate (str): The OCR-recognized string.

    Returns:
        tuple: A tuple containing the best-matching Pochven system name and its index.
    """
    best_score = 0
    best_match = ""
    best_index = -1
    for (i, sys) in enumerate(POCHVEN):
        score = jellyfish.jaro_similarity(ocr_estimate, sys)
        if score > best_score:
            best_match = sys
            best_score = score
            best_index = i

    return best_match, best_index


def next_system(index: int) -> int:
    """
    Determines the index of the next Pochven system in the list.

    Args:
        index (int): The current system's index.

    Returns:
        int: The index of the next Pochven system.
    """
    if index + 1 >= len(POCHVEN) - 3:
        return 0
    else:
        return index + 1


def extract_overview(img_overview):
    """
    Extracts information from the game's overview using OCR.

    Args:
        img_overview (Image): The screenshot of the game's overview.

    Returns:
        list: A list of tuples containing Pochven system names and bounding box coordinates.
    """
    overview = []
    with tesserocr.PyTessBaseAPI() as api:
        level = tesserocr.RIL.WORD
        api.SetImage(img_overview)
        api.Recognize()
        ri = api.GetIterator()
        while True:
            word = ri.GetUTF8Text(level).strip()
            boxes = ri.BoundingBox(level)
            overview.append((match_system(word), boxes))
            if not ri.Next(level):
                break

    return overview


def click_on_gate(gate):
    """
    Simulates a click on a gate position in the game's overview.

    Args:
        gate (tuple): A tuple containing Pochven system information and bounding box coordinates.
    """
    bbox = gate[1]
    middle = [bbox[0], bbox[1]]
    pyautogui.moveTo(middle[0] + region_overview[0], middle[1] + region_overview[1], 0.3 + random.random() * 0.3)
    pyautogui.click(middle[0] + region_overview[0], middle[1] + region_overview[1], 1,
                    duration=0.5 + random.random() * 0.3)


def get_current_system():
    """
    Extracts the current system's information using OCR.

    Returns:
        tuple: A tuple containing the best-matching Pochven system name and its index.
    """
    img_system = grab_win(region_system)
    system = tesserocr.image_to_text(img_system)
    system = system.strip().split(" ")[0].strip()
    system = match_system(system)
    return system


def jump_to_gate(gate):
    """
    Initiates a jump to the next Pochven system by selecting a gate in the overview.

    Args:
        gate (tuple): A tuple containing Pochven system information and bounding box coordinates.
    """
    click_on_gate(gate)

    pyautogui.moveTo(position_jump[0], position_jump[1], 0.3 + random.random() * 0.3)

    # disable for dry run
    pyautogui.click(position_jump[0], position_jump[1], 1, duration=0.5 + random.random() * 0.3)


def explore():
    """
    Initiates exploration of a new Pochven system, captures information, and sends a report to a central server.
    """
    logging.info("EXPLORE NEW SYSTEM")

    img_overview = grab_win(region_overview)
    img_probe = grab_win(region_probe)
    img_dscan = grab_win(region_dscan)

    # OCR Text analysis
    system = get_current_system()
    probe = tesserocr.image_to_text(img_probe)
    dscan = tesserocr.image_to_text(img_dscan)
    try:
        overview = extract_overview(img_overview)  # keep the boxes for the overview,
    except RuntimeError as e:
        print("Error when reading the overview")
        logging.error("Error when reading the overview")
        raise e

    logging.info("System: %s", system[0])
    print(system)
    logging.info("Overview %s", overview)
    print(overview)

    probe = probe.strip().splitlines()
    probe = [p.strip() for p in probe]
    probe = [p for p in probe if p != ""]

    dscan = dscan.strip().splitlines()
    dscan = [p.strip() for p in dscan]
    dscan = [p for p in dscan if p != ""]

    report_dict = {'system': system, 'probe': probe, 'dscan': dscan, 'key': key}

    print(json.dumps(report_dict))

    print("send report")
    x = requests.post(url, json=report_dict, timeout=2.50)
    print("response", x)

    next_index = next_system(system[1])
    next_position = 0
    for i, gate in enumerate(overview):
        if gate[0][1] == next_index:
            next_position = i
            logging.info("fount next gate:  %s", gate)
            break

    logging.info("going to next gate %s", overview[next_position])
    jump_to_gate(overview[next_position])


def jumping():
    """
    Waits for the ship to complete a jump to the next Pochven system.
    """
    logging.info("WAIT FOR JUMP")
    last_system = get_current_system()
    # timeout after 50s
    for _ in range(50):
        current_system = get_current_system()
        pyautogui.sleep(1)
        logging.info("scan for system change:  %s", current_system)
        print(current_system)
        if current_system[1] != -1 and last_system[0] != current_system[0]:
            break


class GracefulKiller:
    kill_now = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, *args):
        self.kill_now = True


if __name__ == '__main__':
    killer = GracefulKiller()
    # server data endpoint config
    with open("destination.txt", "r") as f:
        url = f.read().strip()
    with open("key.txt", "r") as f:
        key = f.read().strip()

    try:
        # screen regions from config
        with open("screen_config.yaml") as file:
            screen_config = yaml.safe_load(file)
            position_jump = screen_config["jump"]
            position_scan = screen_config["scan"]
            region_overview = screen_config["overview"]
            region_dscan = screen_config["dscan"]
            region_system = screen_config["system"]
            region_probe = screen_config["probe"]
    except FileNotFoundError:
        print("screen_config.yaml not found run setup_capture first")
        sys.exit(1)

    # image filter
    threshold = 180

    # setup screenshot engine
    sct = mss.mss()

    # Pochven system list constant
    POCHVEN = import_pochven()

    while not killer.kill_now:
        try:
            explore()
            jumping()
            pyautogui.sleep(5 + random.random() * 3)
        except RuntimeError:
            pyautogui.sleep(5 + random.random() * 3)
            print("Error during operation retry")
            logging.error("Error during operation retry")
            pass
