import json

from textual import on, work
from textual.containers import Horizontal, ScrollableContainer, Vertical
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    Checkbox,
    Collapsible,
    Input,
    Label,
    RadioButton,
    RadioSet,
    Static,
    TextArea,
)

from .file_screen import FilePickButton
from .utils import generate_from_screen, start_cmd


class ServerScreen(ModalScreen):
    CSS_PATH = "style.css"
    config_dict = {}

    def compose(self):
        with ScrollableContainer():
            yield Label("Create server")
            with Collapsible(title="Optional config", id="config"):
                with Horizontal():
                    with Vertical():
                        with Collapsible(title="Sinara server container name"):
                            yield Input(
                                value="jovyan-single-use", name="instanceName"
                            )

                        with Collapsible(title="Memory"):
                            yield Static(
                                "Amount of memory requested"
                                " for server container"
                            )
                            yield Input(value="4g", name="memRequest")

                            yield Static(
                                "Maximum amount of memory for server container"
                            )
                            yield Input(value="8g", name="memLimit")

                            yield Static(
                                "Maximum amount of shared memory for"
                                " server container"
                            )
                            yield Input(value="512m", name="shm_size")

                        with Collapsible(title="Cpu"):
                            yield Static(
                                " Number of CPU cores to use for"
                                " server container"
                            )
                            yield Input(
                                value="4", type="number", name="cpuLimit"
                            )

                        with Collapsible(
                            title="Folders Path (only used in basic mode)"
                        ):
                            yield Static("Path to data fodler on host")
                            yield FilePickButton(name="jovyanDataPath")

                            yield Static("Path to work fodler on host")
                            yield FilePickButton(name="jovyanWorkPath")

                            yield Static("Path to tmp fodler on host")
                            yield FilePickButton(name="jovyanTmpPath")

                    with Vertical():
                        with Collapsible(title="Server config"):
                            yield Checkbox(
                                "Create Folders",
                                value=True,
                                name="createFolders",
                            )
                            yield Checkbox(
                                "Gpu Enabled", value=True, name="gpuEnabled"
                            )
                            yield Checkbox(
                                "Run server without password protection",
                                value=False,
                                name="insecure",
                            )
                            yield Checkbox(
                                "Use expermiental server images",
                                value=False,
                                name="experimental",
                            )

                        with Collapsible(title="Server platform"):
                            yield Static("Host where the server is run")

                            with RadioSet(name="platform"):
                                yield RadioButton("Desktop", value=True)
                                yield RadioButton("Remote VM")

                        with Collapsible(title="Run Mode"):
                            yield Static(
                                "Quick - work, data, tmp will"
                                " be mounted inside docker volumes"
                            )
                            yield Static(
                                "Basic - work, data, tmp will"
                                " be mounted from host folders"
                            )

                            with RadioSet(name="runMode"):
                                yield RadioButton("Quick", value=True)
                                yield RadioButton("Basic")

            yield Static()
            with RadioSet(name="sinara_image_num"):
                yield RadioButton("Sinara for CV", value=True)
                yield RadioButton("Sinara for ML")
            yield Static()

            with Horizontal():
                yield Button(
                    "Create!",
                    id="server_button",
                    classes="button",
                    variant="success",
                )
                yield Button(
                    "Remove!",
                    id="server_remove_button",
                    classes="button",
                    variant="error",
                )
                yield Button(
                    "HELP",
                    id="help_button",
                    classes="button",
                    variant="primary",
                )
                yield Button(
                    "Get config",
                    id="cfg_button",
                    classes="button",
                    variant="success",
                )

            with Horizontal():
                yield Button(
                    "Start!",
                    id="server_start_button",
                    classes="button",
                    variant="success",
                )
                yield Button(
                    "Stop!",
                    id="server_stop_button",
                    classes="button",
                    variant="warning",
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

            yield Static()

            self.static_widget: TextArea = TextArea(
                disabled=True, id="output_text_area", classes="log_window"
            )
            yield self.static_widget

    def generate_config(self):
        result = generate_from_screen(self)
        return result

    @work(thread=True)
    def create_server_cmd(self):
        cmd = "sinara server create --verbose "
        for key, val in self.config_dict.items():
            cmd += f"--{key} '{val}' "

        self.static_widget.clear()

        lines = [" "]
        for decoded_line in start_cmd(cmd):
            if len(decoded_line) > 0:
                if lines[-1][-1] == "\r":
                    lines[-1] = decoded_line
                else:
                    lines.append(decoded_line)

            self.static_widget.load_text("".join([cmd + "\n"] + lines[1:]))

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

    @on(Button.Pressed, "#server_button")
    def server_button(self):
        if self.generate_config():
            self.create_server_cmd()

    @on(Button.Pressed, "#cfg_button")
    def cfg_button(self):
        self.static_widget.clear()
        result = self.generate_config()
        if result:
            self.static_widget.load_text(json.dumps(self.config_dict, indent=4))

    @on(Button.Pressed, "#server_remove_button")
    def server_remove_button(self):
        self.cmd("sinara server remove")

    @on(Button.Pressed, "#server_stop_button")
    def server_stop_button(self):
        self.cmd("sinara server stop")

    @on(Button.Pressed, "#server_start_button")
    def server_start_button(self):
        self.cmd("sinara server start")

    @on(Button.Pressed, "#help_button")
    def help_button(self):
        self.cmd("sinara server create -h")

    @on(Button.Pressed, "#back_button")
    def back_button(self):
        self.dismiss()

    @on(Button.Pressed, "#exit_button")
    def exit_button(self):
        self.parent.exit()
