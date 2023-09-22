"""
Script: Interactive Pochven Screen Setup Utility
Version: 1.0
Copyright (c) 2023 O.Walter

This Python script is designed for configuring screen regions and button positions for a specific task,
likely related to a video game or application. It provides interactive functionality for the user to define and
visualize screen regions and button positions, which can be useful for automating mouse interactions with specific
on-screen elements.

The script enters an infinite loop to repeatedly configure the screen regions and button positions,
capture screenshots, and annotate them. The user is prompted to confirm the configuration, and if confirmed,
the data is saved to a YAML file named "screen_config.yaml."

Usage: 1. Run the script, and it will guide you through the process of configuring screen regions and button
positions. 2. After configuring, the user is prompted to confirm the setup, and the configuration is saved to a YAML
file for later use.

Note: This script requires the installation of several external libraries, including pynput, mss, Pillow (PIL),
matplotlib, and PyYAML.
"""

from pynput import mouse
import mss.tools
from PIL import Image, ImageDraw
from matplotlib import pyplot as plt
import yaml
import time


def wait_for_click():
    """
    Waits for a right-click event and returns the x and y coordinates of the click.

    Returns:
        tuple: A tuple containing the x and y coordinates of the right-click event.
    """
    with mouse.Events() as events:
        for event in events:
            try:
                if event.button == mouse.Button.right and event.pressed == True:
                    print(event)
                    return event.x, event.y
            except AttributeError:
                pass


# init screenshot module
sct = mss.mss()


def ask_ok() -> bool:
    """
    Asks the user if the captured image is okay.

    Returns:
        bool: True if the user responds with 'y' or 'Y', False otherwise.
    """
    data = input("Is the image ok?[y/n]\n")
    return data == "y" or data == 'Y'


def ask_for_position(name):
    """
    Asks the user to right-click on a specific icon and returns the position of the click.

    Args:
        name (str): The name of the icon or element to right-click on.

    Returns:
        tuple: A tuple containing the x and y coordinates of the right-click event.
    """
    print(f"right click on {name} icon")
    pos = wait_for_click()
    return pos


def ask_for_region(name):
    """
    Asks the user to right-click twice to define a region and returns the bounding box coordinates.

    Args:
        name (str): The name of the region being defined.

    Returns:
        tuple: A tuple containing the left, top, width, and height of the bounding box.
    """
    print(f"right click on {name} top left")
    pos_lt = wait_for_click()
    time.sleep(0.2)
    print(f"right click on {name} bottem right")
    pos_br = wait_for_click()
    bbox = (pos_lt[0], pos_lt[1], pos_br[0] - pos_lt[0], pos_br[1] - pos_lt[1])
    return bbox


def draw_rectangle(drawing, bbox, outline):
    """
    Draws a rectangle on an image.

    Args:
        drawing: An ImageDraw object for drawing on an image.
        bbox (tuple): A tuple containing the left, top, width, and height of the bounding box.
        outline (str): The color of the rectangle's outline.

    Returns:
        None
    """
    drawing.rectangle(((bbox[0], bbox[1]),
                       (bbox[0] + bbox[2], bbox[1] + bbox[3])),
                      outline=outline, width=10)


def main():
    while True:
        # button positions
        position_jump = ask_for_position("Jump")
        position_scan = ask_for_position("Scan")

        # screen regions
        region_overview = ask_for_region("Overview")
        region_probe = ask_for_region("Probe Scanner")
        region_system = ask_for_region("System Name")
        region_dscan = ask_for_region("Dscan")

        sct_img = sct.grab(sct.monitors[0])
        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        draw = ImageDraw.Draw(img)

        draw_rectangle(draw, region_overview, 'yellow')
        draw_rectangle(draw, region_probe, 'red')
        draw_rectangle(draw, region_system, 'blue')
        draw_rectangle(draw, region_dscan, 'orange')

        draw.rectangle(((position_jump[0] - 10, position_jump[1] - 10), (position_jump[0] + 20, position_jump[1] + 20)),
                       outline='magenta', width=5)
        draw.rectangle(((position_scan[0] - 10, position_scan[1] - 10), (position_scan[0] + 20, position_scan[1] + 20)),
                       outline='magenta', width=5)

        print("Yellow:\t Overview")
        print("Red:\t Probe-Scanner")
        print("Blue:\t System Name")
        print("Orange:\t Dscan Result")
        print("Magenta:\t Jump and Scan Button ")

        plt.imshow(img)
        plt.show()

        if ask_ok():
            break

    config = {'jump': position_jump,
              'scan': position_scan,
              'overview': region_overview,
              'probe': region_probe,
              'system': region_system,
              'dscan': region_dscan}

    yaml.safe_dump(config, open("screen_config.yaml", "w"))


if __name__ == '__main__':
    main()

