from pathlib import Path

from sinaraml._version import __version__ as sinaraml_version
from textual import on, work
from textual.app import App
from textual.containers import Horizontal
from textual.events import Event
from textual.widgets import Button, Label, Log, Static

try:
    from sinaraX._version import __version__ as sinaraX_version
except ImportError:
    sinaraX_version = "__dev__"

from .running import RunningScreen
from .server import ServerScreen
from .server_cfg import BaseFunctions
from .update import UpdateScreen
from .utils.config import AppConfig
from .utils.infra import (
    check_docker,
    check_docker_group,
    check_last_version,
    check_platform,
)


class SinaraX(App, BaseFunctions):
    CSS_PATH = "style.css"
    system_info_data = None
    config = AppConfig()
    SCREENS = {
        "server_screen": ServerScreen(),
        "update_screen": UpdateScreen(),
        "running_screen": RunningScreen(),
    }

    BINDINGS = [
        ("escape", "exit", "Exit"),
        ("ctrl+s", "save_screen", "Save screenshot"),
    ]

    def action_exit(self):
        self.exit()

    def action_save_screen(self):
        image_folder = Path("./images/")
        image_folder.mkdir(exist_ok=True)
        self.save_screenshot(image_folder.joinpath("main.svg"))

    def compose(self):
        yield Label(
            f"SinaraX by MiXaiLL76; sinaraml=={sinaraml_version};"
            f" sinaraX=={sinaraX_version}"
        )

        with Horizontal():
            yield Button(
                "SERVER",
                id="server_screen_start",
                classes="button",
                variant="primary",
            )

            yield Button(
                "UPDATE",
                id="update_screen_start",
                classes="button",
                variant="primary",
            )

            yield Button(
                "RUNNING",
                id="running_screen_start",
                classes="button",
                variant="primary",
            )

        with Horizontal():
            yield Button(
                "Check system",
                id="check_button",
                classes="button",
                variant="primary",
            )
            yield Button(
                "Exit",
                id="exit_button",
                classes="exit_button button",
                variant="warning",
            )

        yield Static()

        self.log_window: Log = Log(
            highlight=True, id="main_log_window", classes="log_window"
        )
        yield self.log_window

        if self.system_info_data is None:
            self.get_system_info()

    @work(thread=True)
    def get_system_info(self):
        self.system_info_data = {
            "docker_info": check_docker(),
            "platform_info": check_platform(),
            "group_info": check_docker_group(),
            "sinaraX": (
                check_last_version("sinaraX")
                if sinaraX_version != "__dev__"
                else (True, "Dev")
            ),
            "sinaraml": check_last_version("sinaraml"),
        }
        lines = []
        if self.system_info_data["docker_info"]["ok"]:
            docker_version = self.system_info_data["docker_info"][
                "ServerVersion"
            ]
            lines.append(f"Docker is running : True ; {docker_version}")
            for _docker_err in self.system_info_data["docker_info"][
                "ServerErrors"
            ]:
                lines.append(_docker_err)

        else:
            lines.append("Docker is running : False")
            self.notify("Docker is not running!", severity="error", timeout=2)

        if self.system_info_data["group_info"]["username"]:
            _USER = self.system_info_data["group_info"]["username"]
            lines.append(f"System user : {_USER}")

            docker_group = self.system_info_data["group_info"]["docker_group"]
            lines.append(f"Docker group created : {docker_group}")
            if not docker_group:
                self.notify(
                    "Docker group not created!", severity="warning", timeout=2
                )

            user_in_group = self.system_info_data["group_info"]["user_in_group"]
            lines.append(f"{_USER} in group docker : {user_in_group}")
            if not docker_group:
                self.notify(
                    f"{_USER} not in group docker",
                    severity="warning",
                    timeout=2,
                )

        _platform = self.system_info_data["platform_info"]["platform"]

        if self.system_info_data["platform_info"]["ok"]:
            lines.append(f"Platform : True ; {_platform}")
        else:
            lines.append(f"Platform : False ; {_platform} USE WSL or Linux!")
            self.notify("Platform not valid!", severity="error", timeout=2)

        lines.append(
            f"sinaraX : {self.system_info_data['sinaraX'][0]} ;"
            f" {self.system_info_data['sinaraX'][1]}"
        )
        lines.append(
            f"sinaraml : {self.system_info_data['sinaraml'][0]} ;"
            f" {self.system_info_data['sinaraml'][1]}"
        )

        # map strings
        max_index = -1
        for line in lines:
            _idx = line.find(":")
            if _idx > max_index:
                max_index = _idx

        for i, line in enumerate(lines):
            _idx = line.find(":")
            lines[i] = line[:_idx] + " " * (max_index - _idx) + line[_idx:]

        self.write_log_lines(lines)

    @on(Button.Pressed, "#check_button")
    def check_button(self):
        self.system_info_data = None
        self.get_system_info()

    @on(Button.Pressed, "#server_screen_start")
    def server_screen_start(self):
        self.push_screen("server_screen")

    @on(Button.Pressed, "#update_screen_start")
    def update_screen_start(self):
        self.push_screen("update_screen")

    @on(Button.Pressed, "#running_screen_start")
    def running_screen_start(self):
        self.push_screen("running_screen")

    @on(Button.Pressed, "#exit_button")
    def exit_button(self):
        self.exit()

    def on_event(self, event: Event):
        self.app.refresh(layout=True)
        return super().on_event(event)
