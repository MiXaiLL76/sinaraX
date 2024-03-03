from textual import on
from textual.app import App
from textual.containers import Horizontal
from textual.widgets import Button, Label

from .server import ServerScreen


class SinaraX(App):
    CSS_PATH = "style.css"

    def compose(self):
        yield Label("SinaraML TUI by MiXaiLL76")
        yield Horizontal(
            Button(
                "SERVER",
                id="create_server_button",
                classes="button",
                variant="primary",
            ),
            Button(
                "Exit",
                id="exit_button",
                classes="exit_button button",
                variant="warning",
            ),
        )

    @on(Button.Pressed, "#create_server_button")
    def create_server_button(self):
        self.push_screen(ServerScreen())

    @on(Button.Pressed, "#exit_button")
    def exit_button(self):
        self.exit()
