from pathlib import Path

from textual import on
from textual.containers import Horizontal, ScrollableContainer
from textual.screen import ModalScreen
from textual.widget import Widget
from textual.widgets import Button, DirectoryTree, Input, Label, Static

from ..utils.custom import FilteredDirectoryTree


class FilePickButton(Widget, can_focus=True):
    DEFAULT_CSS = """
    FilePickButton{
        height: auto;
    }
    FilePickButton > Horizontal > .file-pick-label{
        height: auto;
        padding: 0 2;
        border: none;
        min-width: 5;
        max-width: 95%;
        width: 85%;
        margin-left: 1;
    }
    FilePickButton > Horizontal > .file-pick-button{
        min-width: 5;
        border: none;
        padding: 0;
        margin: 0;
        &:hover {
            border: none;
        }
        &.-active {
            border: none;
        }
    }
    FilePickButton > Horizontal{
        margin-bottom: 1;
    }
    """

    value = ""

    def compose(self):
        with Horizontal():
            self.input = Input(classes="file-pick-label")
            yield self.input
            yield Button("F", classes="file-pick-button", variant="primary")

    @on(Button.Pressed)
    def open_file_tree_screen(self):
        def on_exit(selected_path: str) -> None:
            self.value = str(selected_path)
            self.input.value = self.value

        self.app.push_screen(FileTreeScreen(), on_exit)

    @on(Input.Changed)
    def input_change(self, event: Input.Changed) -> None:
        self.value = event.value


class FileTreeScreen(ModalScreen[str | None]):
    DEFAULT_CSS = """
    """

    selected_path = None

    @on(Button.Pressed, ".back_button")
    def back_button(self):
        self.dismiss(self.selected_path)

    @on(Button.Pressed, "#exit_button")
    def exit_button(self):
        self.parent.exit()

    @on(DirectoryTree.DirectorySelected)
    def select_record(self, event: DirectoryTree.DirectorySelected) -> None:
        self.selected_path = event.path.as_posix()
        self.static_path.update(self.selected_path)

    def compose(self):
        self.static_path = Static("[]")

        with Horizontal():
            yield Label("Selected path:")
            yield self.static_path

        with ScrollableContainer():
            with Horizontal():
                yield Button(
                    "OK",
                    id="ok_button",
                    classes="back_button button",
                    variant="success",
                )
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
            yield FilteredDirectoryTree(Path().home().as_posix())
