from pathlib import Path

from textual import on
from textual.containers import Horizontal, Vertical
from textual.events import Mount
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    Checkbox,
    Collapsible,
    Footer,
    Input,
    Log,
    RadioButton,
    RadioSet,
    Static,
    TabbedContent,
    TabPane,
)

from .server_cfg import BaseFunctions

class ModelScreen(ModalScreen, BaseFunctions):
    CSS_PATH = "style.css"
    config_dict = {}

    BINDINGS = [
        ("escape", "app.pop_screen"),
        ("ctrl+s", "save_screen"),
        ("f1", "load_config", "Load cfg"),
        ("f6", "copy_logs", "Copy log to clipboard"),
        ("u", ""),
        ("s", ""),
    ]

    def compose(self):
        yield Footer()

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

        self.log_window: Log = Log(highlight=True, classes="log_window")
        yield self.log_window

    @on(Button.Pressed, "#help_button")
    def help_button(self):
        self.cmd("sinara model containerize -h")

    @on(Button.Pressed, "#back_button")
    def back_button(self):
        self.log_window.clear()
        self.dismiss()

    @on(Button.Pressed, "#exit_button")
    def exit_button(self):
        self.parent.exit()