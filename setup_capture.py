from pynput import mouse
import mss.tools
from PIL import Image
from matplotlib import pyplot as plt
import yaml
import time


def wait_for_click():
    with mouse.Events() as events:
        for event in events:
            try:
                if event.button == mouse.Button.right:
                    print(event)
                    return event.x, event.y
            except AttributeError:
                pass


sct = mss.mss()


def grab_win(bbox):
    monitor = {"top": bbox[1], "left": bbox[0], "width": bbox[2], "height": bbox[3]}
    print(monitor)
    sct_img = sct.grab(monitor)
    img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
    return img


def test_win(bbox):
    img = grab_win(bbox)
    plt.imshow(img)
    plt.show()


def ask_ok() -> bool:
    data = input("Is the image ok?[y/n]\n")
    return data == "y" or data == 'Y'


def ask_for_positon(name):
    while True:
        print(f"right click on {name} icon")
        pos = wait_for_click()
        bbox = [pos[0] - 40, pos[1] - 40, 80, 80]
        test_win(bbox)
        if ask_ok():
            return pos


def ask_for_region(name):
    while True:
        print(f"right click on {name} top left")
        poslt = wait_for_click()
        time.sleep(0.2)
        print(f"right click on {name} bottem right")
        posbr = wait_for_click()
        bbox = (poslt[0], poslt[1], posbr[0] - poslt[0], posbr[1] - poslt[1])
        test_win(bbox)
        if ask_ok():
            return bbox


if __name__ == '__main__':

    # button positions
    position_jump = ask_for_positon("Jump")
    position_scan = ask_for_positon("Scan")

    # screen regions
    region_overview = ask_for_region("Overview")
    region_probe = ask_for_region("Probe Scanner")
    region_system = ask_for_region("System Name")
    region_dscan = ask_for_region("Dscan")

    config = {'jump': position_jump,
              'scan': position_scan,
              'overview': region_overview,
              'probe': region_probe,
              'system': region_system,
              'dscan': region_dscan}

    yaml.safe_dump(config, open("screen_config.yaml", "w"))
