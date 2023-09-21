from pynput import mouse
import pynput

f = open("coordinates.log", "w")

def on_click(x, y, button, pressed):
    print(x,y,pressed)
    if pressed:
        f.write(f"{x},{y}\n")
        f.flush()


listener = mouse.Listener(
    on_move=None,
    on_click=on_click,
    on_scroll=None)
listener.start()


while True:
    pass