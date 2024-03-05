from textual import on, work
from textual.containers import Horizontal, ScrollableContainer
from textual.screen import ModalScreen
from textual.widgets import Button, Label, TextArea

from .utils import start_cmd


class UpdateScreen(ModalScreen):
    CSS_PATH = "style.css"

    def compose(self):
        with ScrollableContainer():
            yield Label("Update dependencies")

            with Horizontal():
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

            self.static_widget: TextArea = TextArea(
                disabled=True, id="output_text_area", classes="log_window"
            )
            yield self.static_widget

    @work(thread=True)
    def cmd(self, cmd: str):
        self.static_widget.clear()
        lines = [" "]
        for decoded_line in start_cmd(cmd):
            if len(decoded_line) > 0:
                if lines[-1][-1] == "\r":
                    lines[-1] = decoded_line
                else:
                    lines.append(decoded_line)

            self.static_widget.load_text("".join([cmd + "\n"] + lines[1:]))

    @on(Button.Pressed, "#update_sinaraml")
    def update_sinaraml(self):
        self.cmd("pip install sinaraml --upgrade")

    @on(Button.Pressed, "#update_sinaraX")
    def update_sinaraX(self):
        self.cmd("pip install sinaraX --upgrade")

    @on(Button.Pressed, "#back_button")
    def back_button(self):
        self.dismiss()

    @on(Button.Pressed, "#exit_button")
    def exit_button(self):
        self.parent.exit()
