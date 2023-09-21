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

logging.basicConfig(filename='pylot.log', encoding='utf-8', level=logging.DEBUG, format='%(asctime)s %(message)s')

# --------------------- SETUP -----------------------
# 1. setup Overview with gates only
# 2. setup DScan with ships only
# 3. setup Probe scaner only for Anomalies
# 4. put client in Potato mode Ctrl+Shift+F9
# 5. Calibrate screen regions below
# 6. Undock and start this script
# --------------------------------------------------

# server data endpoint config
with open("destination.txt", "r") as f:
    url = f.read().strip()
with open("key.txt", "r") as f:
    key = f.read().strip()

# screen regions from config
with open("screen_config.yaml") as file:
    screen_config = yaml.safe_load(file)
    position_jump = screen_config["jump"]
    position_scan = screen_config["scan"]
    region_overview = screen_config["overview"]
    region_dscan = screen_config["dscan"]
    region_system = screen_config["system"]
    region_probe = screen_config["probe"]

# image filter
threshold = 180

# setup fastgrap screenshot engine
sct = mss.mss()


def grab_win(bbox):
    monitor = {"top": bbox[1], "left": bbox[0], "width": bbox[2], "height": bbox[3]}
    sct_img = sct.grab(monitor)
    img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX").convert("L").point(
        lambda p: p if p > threshold else 0)
    return img


# import pochven system list form textfile
def import_pochven() -> list:
    with open("pochven.txt", "r") as f:
        return [line.strip() for line in f.readlines()]


# Pochven system list constant
POCHVEN = import_pochven()


# get the best matching system same for the ocr input
# also get the system number for naviagtion
def match_system(ocr_estimate: str) -> (str, int):
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


# get the next system number
def next_system(index: int) -> int:
    if index + 1 >= len(POCHVEN) - 3:
        return 0
    else:
        return index + 1


# OCR for the overview with pixel coordinates
def extract_overview(img_overview):
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


# click on the given gate position in the overview
def click_on_gate(gate):
    bbox = gate[1]
    middle = [bbox[0], bbox[1]]
    pyautogui.moveTo(middle[0] + region_overview[0], middle[1] + region_overview[1], 0.3 + random.random() * 0.3)
    pyautogui.click(middle[0] + region_overview[0], middle[1] + region_overview[1], 1,
                    duration=0.5 + random.random() * 0.3)


# ocr, cleanup and matching to get the current position
def get_current_system():
    img_system = grab_win(region_system)
    system = tesserocr.image_to_text(img_system)
    system = system.strip().split(" ")[0].strip()
    system = match_system(system)
    # plt.imshow(img_system)
    # plt.show()
    return system


# jump to the next system.
# select gate in overview and then jump to it
def jump_to_gate(gate):
    click_on_gate(gate)

    pyautogui.moveTo(position_jump[0], position_jump[1], 0.3 + random.random() * 0.3)

    # disable for dry run
    pyautogui.click(position_jump[0], position_jump[1], 1, duration=0.5 + random.random() * 0.3)


def explore():
    logging.info("EXPLORE NEW SYSTEM")

    img_overview = grab_win(region_overview)
    img_probe = grab_win(region_probe)
    img_dscan = grab_win(region_dscan)

    # OCR Text analysis
    system = get_current_system()
    probe = tesserocr.image_to_text(img_probe)
    dscan = tesserocr.image_to_text(img_dscan)
    overview = extract_overview(img_overview)  # keep the boxes for the overview,

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


# wait for the ship to jump to the next system
def jumping():
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


if __name__ == '__main__':
    while True:
        explore()
        jumping()
        pyautogui.sleep(5 + random.random() * 3)
