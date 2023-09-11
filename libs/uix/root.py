import json

from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager

from libs.applibs import utils


class Root(ScreenManager):
    history = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_keyboard=self._handle_keyboard)
        with open(utils.abs_path("screens.json")) as f:
            self.screens_data = json.load(f)

    def _handle_keyboard(self, instance, key, *args):
        if key == 27:
            self.pop()
            return True

    def load_screen(self, screen_name):
        """
        This method creates an instance of the screen object and adds
        it to the screen manager without making it the current screen.

        It is useful in situations where certain state needs
        to be passed to that screen.
        """

        if not self.has_screen(screen_name):
            screen = self.screens_data[screen_name]
            Builder.load_file(utils.abs_path(screen["kv"]))
            exec(screen["import"])
            screen_object = eval(screen["object"])
            screen_object.name = screen_name
            self.add_widget(screen_object)

    def push(self, screen_name, side="left"):
        """
        Appends the screen to the navigation history and
        sets `screen_name` it as the current screen.
        """

        if self.current != screen_name:
            self.history.append({"name": screen_name, "side": side})

        self.load_screen(screen_name)

        self.transition.direction = side

        self.current = screen_name

    def push_replacement(self, screen_name, side="left"):
        """
        Clears the navigation history and sets the
        current screen to `screen_name`.
        """

        self.history.clear()
        self.push(screen_name, side)

    def pop(self):
        """
        Removes the current screen from the navigation history and
        sets the current screen to the previous one.

        To navigate back to the previous screen, use the this method.

        It is automatically triggered when the user presses the back button on
        a mobile device or the ESC button on a desktop.

        Avoid using `scr_mgr_instance.push('prev_screen_name', side='right')`
        as it will collapse the navigation history of the screen manager
        instead use this method.
        """

        if not len(self.history) > 1:
            return

        cur_side = self.history.pop()["side"]
        prev_screen = self.history[-1]

        if cur_side == "left":
            side = "right"
        elif cur_side == "right":
            side = "left"
        elif cur_side == "up":
            side = "down"
        elif cur_side == "down":
            side = "up"

        self.transition.direction = side

        self.current = prev_screen["name"]
