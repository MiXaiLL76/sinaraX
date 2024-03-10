from pathlib import Path

from textual import on
from textual.containers import Horizontal, ScrollableContainer
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Log

from .server_cfg import BaseFunctions


class UpdateScreen(ModalScreen, BaseFunctions):
    CSS_PATH = "style.css"

    BINDINGS = [
        ("escape", "app.pop_screen", "Back to main."),
        ("ctrl+s", "save_screen", "Save screenshot"),
    ]

    def action_save_screen(self):
        image_folder = Path("./images/")
        image_folder.mkdir(exist_ok=True)
        self.app.save_screenshot(image_folder.joinpath("update.svg"))

    def compose(self):
        with ScrollableContainer():
            yield Label("Update dependencies")

            yield Button(
                "Update sinaraml cli",
                id="update_sinaraml",
                classes="button",
                variant="primary",
            )

            yield Button(
                "Update sinaraX",
                id="update_sinaraX",
                classes="button",
                variant="primary",
            )

            with Horizontal():
                yield Button(
                    "< Back",
                    id="back_button",
                    classes="back_button button",
                    variant="primary",
                )
                yield Button(
                    "Exit",
                    id="exit_button",
                    classes="exit_button button",
                    variant="error",
                )

            self.log_window: Log = Log(
                highlight=True, id="output_text_area", classes="log_window"
            )
            yield self.log_window

    @on(Button.Pressed, "#update_sinaraml")
    def update_sinaraml(self):
        self.cmd("pip install sinaraml --upgrade")

    @on(Button.Pressed, "#update_sinaraX")
    def update_sinaraX(self):
        self.cmd("pip install sinaraX --upgrade")

    @on(Button.Pressed, "#back_button")
    def back_button(self):
        self.log_window.clear()
        self.dismiss()

    @on(Button.Pressed, "#exit_button")
    def exit_button(self):
        self.parent.exit()
