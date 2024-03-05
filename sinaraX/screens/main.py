from sinaraml._version import __version__ as sinaraml_version
from textual import on, work
from textual.app import App
from textual.containers import Horizontal
from textual.widgets import Button, Label, Static

from sinaraX._version import __version__ as sinaraX_version

from .server import ServerScreen
from .utils.infra import check_docker, check_docker_group, check_platform


class SinaraX(App):
    CSS_PATH = "style.css"
    system_info_data = None

    def compose(self):
        yield Label(
            f"SinaraX by MiXaiLL76; sinaraml=={sinaraml_version};"
            f" sinaraX=={sinaraX_version}"
        )

        with Horizontal():
            yield Button(
                "SERVER",
                id="create_server_button",
                classes="button",
                variant="primary",
            )

            yield Button(
                "Exit",
                id="exit_button",
                classes="exit_button button",
                variant="warning",
            )

        self.docker_info = Static("Docker version: ")
        self.system_user = Static("System user\t\t\t: not found!")
        self.docker_group = Static("Docker group created\t\t: False")
        self.user_in_docker = Static("USER in group docker\t: False")
        self.system_platform = Static("Platform: not valid!")
        yield self.docker_info
        yield self.system_user
        yield self.docker_group
        yield self.user_in_docker
        yield self.system_platform

    @work(thread=True)
    def get_system_info(self):
        if self.system_info_data is None:
            self.system_info_data = {
                "docker_info": check_docker(),
                "platform_info": check_platform(),
                "group_info": check_docker_group(),
            }

        if self.system_info_data["docker_info"]["ok"]:
            self.docker_info.update(
                "Docker version\t\t\t: "
                + self.system_info_data["docker_info"]["ServerVersion"]
            )
            self.docker_info.set_classes("")
        else:
            self.docker_info.set_classes("not_valid")
            self.docker_info.update("Docker not running!")

        if self.system_info_data["group_info"]["username"]:
            _USER = self.system_info_data["group_info"]["username"]
            self.system_user.update(f"System user\t\t\t: {_USER}")

            self.docker_group.update(
                "Docker group created\t\t:"
                f" {self.system_info_data['group_info']['docker_group']}"
            )
            if self.system_info_data["group_info"]["docker_group"]:
                self.docker_group.set_classes("")
            else:
                self.docker_group.set_classes("not_valid")

            self.user_in_docker.update(
                f"{_USER} in group docker\t:"
                f" {self.system_info_data['group_info']['user_in_group']}"
            )
            if self.system_info_data["group_info"]["user_in_group"]:
                self.user_in_docker.set_classes("")
            else:
                self.user_in_docker.set_classes("not_valid")

        if self.system_info_data["platform_info"]["ok"]:
            self.system_platform.update(
                "Platform\t\t\t: OK!"
                f" {self.system_info_data['platform_info']['platform']}"
            )
            self.system_platform.set_classes("")
        else:
            self.system_platform.update(
                "Platform\t\t\t: NOT VALID!"
                f" {self.system_info_data['platform_info']['platform']}. USE"
                " WSL!"
            )
            self.system_platform.set_classes("not_valid")

    def post_display_hook(self):
        self.get_system_info()

    @on(Button.Pressed, "#create_server_button")
    def create_server_button(self):
        self.push_screen(ServerScreen())

    @on(Button.Pressed, "#exit_button")
    def exit_button(self):
        self.exit()
