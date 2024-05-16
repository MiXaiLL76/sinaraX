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

from .file_screen import FilePickButton
from .server_cfg import ServerFunctions
from .utils import (
    FilteredConfigTree,
    get_cpu_cores_limit,
    get_memory_size_limit,
)


class ServerScreen(ModalScreen, ServerFunctions):
    CSS_PATH = "style.css"
    config_dict = {}

    BINDINGS = [
        ("escape", "app.pop_screen"),
        ("ctrl+s", "save_screen"),
        ("f1", "load_config", "Load cfg"),
        ("f2", "create_server", "Server Create"),
        ("f3", "start_server", "Start"),
        ("f4", "stop_server", "Stop"),
        ("f5", "stop_remove", "Remove"),
        ("f6", "copy_logs", "Copy log to clipboard"),
        ("u", ""),
        ("s", ""),
    ]

    def action_save_screen(self):
        image_folder = Path("./images/")
        image_folder.mkdir(exist_ok=True)
        self.app.save_screenshot(image_folder.joinpath("server.svg"))

    def compose(self):
        yield Footer()
        with TabbedContent(initial="server_tab"):
            with TabPane("Server", id="server_tab"):
                yield Static("Ready configs [~/.sinaraX]:")
                self.config_tree = FilteredConfigTree(
                    Path().home().joinpath(".sinaraX/"), id="ready_configs"
                )
                self.selected_config_path = ""
                yield self.config_tree

                with Horizontal():
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
                    yield Button(
                        "Print config",
                        id="get_cfg_button",
                        classes="button",
                        variant="success",
                    )

                yield Static("Server: ")

                with Horizontal():
                    yield Button(
                        "Create!",
                        id="server_create_button",
                        classes="button",
                        variant="success",
                    )
                    yield Button(
                        "Start!",
                        id="server_start_button",
                        classes="button",
                        variant="success",
                    )
                    yield Button(
                        "Update image",
                        id="update_image_button",
                        classes="button",
                        variant="success",
                    )

                with Horizontal():
                    yield Button(
                        "Remove!",
                        id="server_remove_button",
                        classes="button",
                        variant="error",
                    )
                    yield Button(
                        "Stop!",
                        id="server_stop_button",
                        classes="button",
                        variant="warning",
                    )

            with TabPane("Config", id="config_tab"):
                yield Button(
                    "Save config",
                    id="save_cfg_button",
                    classes="button",
                    variant="success",
                )
                with TabbedContent(initial="base"):
                    with TabPane("Base", id="base"):
                        with Collapsible(
                            title="Sinara server container and config name",
                            collapsed=False,
                        ):
                            yield Input(
                                value="jovyan-single-use",
                                name="instanceName",
                            )

                        with Horizontal():
                            with Vertical():
                                with Collapsible(
                                    title=(
                                        "Host where the server is run"
                                        " (disabled!)"
                                    ),
                                    collapsed=False,
                                ):
                                    with RadioSet(
                                        name="platform",
                                        disabled=True,
                                    ):
                                        yield RadioButton("Desktop", value=True)
                                        yield RadioButton("Remote")

                            with Vertical():
                                with Collapsible(
                                    title="Sinara image for", collapsed=False
                                ):
                                    with RadioSet(name="sinara_image_num"):
                                        yield RadioButton("CV", value=True)
                                        yield RadioButton("ML")

                    with TabPane("Resource", id="resource"):
                        sinara_mem = (
                            get_memory_size_limit() // 1024 // 1024 // 1024
                        )
                        base_shm_size = sinara_mem // 6
                        if base_shm_size < 1:
                            base_shm_size = 1

                        with Collapsible(title="Memory", collapsed=False):
                            yield Static(
                                "Maximum amount of memory for server container"
                                " (GB)"
                            )
                            yield Input(
                                value=str(sinara_mem),
                                type="number",
                                name="memLimit",
                            )

                            yield Static(
                                "Maximum amount of shared memory for"
                                " server container"
                            )
                            yield Input(
                                value=str(base_shm_size) + "g",
                                name="shm_size",
                            )

                        with Collapsible(title="Cpu", collapsed=False):
                            yield Static(
                                " Number of CPU cores to use for"
                                " server container"
                            )
                            yield Input(
                                value=str(get_cpu_cores_limit()),
                                type="number",
                                name="cpuLimit",
                            )

                    with TabPane("Extra", id="extra"):
                        with Collapsible(
                            title="Server config", collapsed=False
                        ):
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

                        with Collapsible(title="Run Mode", collapsed=False):
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

    @on(Button.Pressed, "#server_create_button")
    def server_create_button(self):
        if self.generate_config():
            cmd = "sinara server create --verbose "
            for key, val in self.config_dict.items():
                if type(val) is str:
                    val = f"'{val}'"
                elif type(val) is int:
                    val = f"{val}"
                else:
                    continue

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

    def action_create_server(self):
        self.server_create_button()

    def action_start_server(self):
        self.server_start_button()

    def action_stop_server(self):
        self.server_stop_button()

    def action_remove_server(self):
        self.server_remove_button()

    def action_load_config(self):
        self.load_cfg_button()

    def _on_mount(self, event: Mount) -> None:
        first_node = self.config_tree.get_node_at_line(1)
        if first_node is not None:
            self.selected_config_path = first_node.data.path.as_posix()
            self.config_tree.select_node(first_node)

        return super()._on_mount(event)
