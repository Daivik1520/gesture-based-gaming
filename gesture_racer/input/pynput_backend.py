from pynput.keyboard import Controller as KeyboardController
from pynput.keyboard import Key
from pynput.mouse import Controller as MouseController, Button

from gesture_racer.input.base import KeyboardMouseInput


class PynputInput(KeyboardMouseInput):
    def __init__(self):
        super().__init__()
        self.keyboard = KeyboardController()
        self.mouse = MouseController()

    def press(self, key: str):
        try:
            self.keyboard.press(key)
        except Exception:
            pass

    def release(self, key: str):
        try:
            self.keyboard.release(key)
        except Exception:
            pass

    def click_mouse(self, button: str = 'left'):
        try:
            btn = Button.left if button == 'left' else Button.right
            self.mouse.click(btn)
        except Exception:
            pass

    def move_mouse(self, dx: float, dy: float):
        try:
            self.mouse.move(dx, dy)
        except Exception:
            pass