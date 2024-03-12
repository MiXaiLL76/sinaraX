from pathlib import Path

from textual import on
from textual.containers import Horizontal, ScrollableContainer, Vertical
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    Checkbox,
    Collapsible,
    Input,
    Label,
    Log,
    RadioButton,
    RadioSet,
    Static,
)

from .file_screen import FilePickButton
from .server_cfg import ServerFunctions
from .utils import FilteredConfigTree


class ServerScreen(ModalScreen, ServerFunctions):
    CSS_PATH = "style.css"
    config_dict = {}

    BINDINGS = [
        ("escape", "app.pop_screen", "Back to main."),
        ("ctrl+s", "save_screen", "Save screenshot"),
    ]

    def action_save_screen(self):
        image_folder = Path("./images/")
        image_folder.mkdir(exist_ok=True)
        self.app.save_screenshot(image_folder.joinpath("server.svg"))

    def compose(self):
        with ScrollableContainer():
            yield Label("Create server")
            with Collapsible(title="Optional config", id="config"):
                with Horizontal(id="config_horizontal"):
                    with Vertical():
                        with Collapsible(
                            title="Sinara server container and config name"
                        ):
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

                    with Vertical():
                        with Collapsible(title="Server config"):
                            yield Checkbox(
                                "Create Folders (disabled!)",
                                value=True,
                                name="createFolders",
                                disabled=True,
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

                            with RadioSet(name="runMode", id="run_mode"):
                                yield RadioButton("Quick", value=True)
                                yield RadioButton("Basic")

                            yield Static(
                                "Path to parent folder for data, work and tmp"
                            )
                            self.jovyanRootPath_picker = FilePickButton(
                                name="jovyanRootPath", disabled=True
                            )
                            yield self.jovyanRootPath_picker

            with Horizontal():
                with Vertical():
                    yield Static("Sinara image for:")
                    with RadioSet(name="sinara_image_num"):
                        yield RadioButton("CV", value=True)
                        yield RadioButton("ML")
                with Vertical():
                    yield Static("Ready configs [~/.sinaraX]:")
                    self.config_tree = FilteredConfigTree(
                        Path().home().joinpath(".sinaraX/"), id="ready_configs"
                    )
                    self.selected_config_path = ""
                    yield self.config_tree

                    self.config_tree.children
                    with Horizontal():
                        yield Button(
                            "Save config",
                            id="save_cfg_button",
                            classes="button",
                            variant="success",
                        )
                        yield Button(
                            "Load selected",
                            id="load_cfg_button",
                            classes="button",
                            variant="primary",
                        )
                        yield Button(
                            "Remove selected",
                            id="remove_cfg_button",
                            classes="button",
                            variant="error",
                        )

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
                    "Update image",
                    id="update_image_button",
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
                yield Button(
                    "Get config",
                    id="get_cfg_button",
                    classes="button",
                    variant="success",
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

            self.log_window: Log = Log(
                highlight=True, id="output_text_area", classes="log_window"
            )
            yield self.log_window

    @on(Button.Pressed, "#server_button")
    def server_button(self):
        if self.generate_config():
            cmd = "sinara server create --verbose "
            for key, val in self.config_dict.items():
                if len(val) > 1:
                    val = f"'{val}'"

                cmd += f"--{key} {val} "

            self.cmd(cmd)

    @on(Button.Pressed, "#server_remove_button")
    def server_remove_button(self):
        cmd = "sinara server remove"
        result = self.generate_config()
        if result:
            if self.config_dict.get("instanceName"):
                cmd += " --instanceName " + str(
                    self.config_dict.get("instanceName")
                )

        self.cmd(cmd)

    @on(Button.Pressed, "#server_stop_button")
    def server_stop_button(self):
        cmd = "sinara server stop"
        result = self.generate_config()
        if result:
            if self.config_dict.get("instanceName"):
                cmd += " --instanceName " + str(
                    self.config_dict.get("instanceName")
                )

        self.cmd(cmd)

    @on(Button.Pressed, "#server_start_button")
    def server_start_button(self):
        cmd = "sinara server start"
        result = self.generate_config()
        if result:
            if self.config_dict.get("instanceName"):
                cmd += " --instanceName " + str(
                    self.config_dict.get("instanceName")
                )

        self.cmd(cmd)

    @on(Button.Pressed, "#update_image_button")
    def update_image_button(self):
        cmd = "sinara server update"
        result = self.generate_config()
        if result:
            image = self.config_dict.get("image")
            if image:
                cmd += " --image "
                if "cv" in image:
                    cmd += "cv "
                else:
                    cmd += "ml "

                if "exp" in image:
                    cmd += "--experimental"
            else:
                cmd += " -h"

        self.cmd(cmd)

    @on(Button.Pressed, "#help_button")
    def help_button(self):
        self.cmd("sinara server create -h")

    @on(Button.Pressed, "#back_button")
    def back_button(self):
        self.log_window.clear()
        self.dismiss()

    @on(Button.Pressed, "#exit_button")
    def exit_button(self):
        self.parent.exit()

    @on(FilteredConfigTree.FileSelected)
    def select_config(self, event: FilteredConfigTree.FileSelected):
        return super().select_config(event)

    @on(Button.Pressed, "#remove_cfg_button")
    def remove_config_file_button(self):
        return super().remove_config_file_button()

    @on(Button.Pressed, "#load_cfg_button")
    def load_cfg_button(self):
        return super().load_cfg_button()

    @on(Button.Pressed, "#get_cfg_button")
    def get_cfg_button(self):
        return super().get_cfg_button()

    @on(Button.Pressed, "#save_cfg_button")
    def save_cfg_button(self):
        return super().save_cfg_button()

    @on(RadioSet.Changed, "#run_mode")
    def changed_visible(self, event: RadioSet.Changed):
        if event.index == 1:
            self.jovyanRootPath_picker.disabled = False
        else:
            self.jovyanRootPath_picker.disabled = True
