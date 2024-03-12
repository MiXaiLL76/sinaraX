from pathlib import Path

from textual import on, work
from textual.containers import Horizontal, ScrollableContainer
from textual.screen import ModalScreen
from textual.widgets import Button, Collapsible, DataTable, Label, Log, Static

from .server_cfg import BaseFunctions
from .utils.infra import get_instanse_token, get_sinara_servers
from .utils.process import decode_lines


class RunningScreen(ModalScreen, BaseFunctions):
    CSS_PATH = "style.css"

    BINDINGS = [
        ("escape", "app.pop_screen", "Back to main."),
        ("ctrl+s", "save_screen", "Save screenshot"),
    ]

    def action_save_screen(self):
        image_folder = Path("./images/")
        image_folder.mkdir(exist_ok=True)
        self.app.save_screenshot(image_folder.joinpath("running.svg"))

    def compose(self):
        self.selected_uid = None

        with ScrollableContainer():
            yield Label("Running servers:")
            yield Static("Click on server for inspect server url.")
            yield DataTable(cursor_type="row")

            yield Static()

            with Collapsible(title="not supported by sinaraml"):
                yield Static("Select server in click!")
                self.sudo_button = Button(
                    "install sudo",
                    id="install_sudo",
                    classes="button",
                    disabled=True,
                )
                yield self.sudo_button

            yield Button(
                "Refresh servers",
                id="refresh_button",
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

            self.log_window: Log = Log(
                highlight=True,
                id="running_screen_log_window",
                classes="log_window",
            )
            yield self.log_window

    @work(thread=True)
    def mount_servers(self):
        servers = get_sinara_servers()
        table = self.query_one(DataTable)
        table.clear()
        table.columns.clear()

        if len(servers[0]) > 0:
            table.add_columns(*servers[0])
            table.add_rows(servers[1:])

    def on_mount(self) -> None:
        self.mount_servers()

    @on(Button.Pressed, "#refresh_button")
    def refresh_button(self):
        self.mount_servers()

    @work(thread=True)
    def select_server(self, row):
        instanceName = row[1]
        port = row[2]
        server_url = get_instanse_token(instanceName, port)
        out_string = f"{instanceName} running on: {server_url}\n"
        self.log_window.write_line(out_string)
        self.log_window.write_line("-----")

    @on(DataTable.RowSelected)
    def on_row_selected(self, event: DataTable.RowSelected):
        row = event.data_table.get_row_at(event.cursor_row)
        self.select_server(row)
        self.sudo_button.disabled = False
        self.selected_uid = row[0]

    @work(thread=True)
    def install_sudo(self, uid):
        exec_cmd = "docker exec -it -u root {uid} bash -c '{cmd}'"
        cmds = [
            "rm -rf /etc/apt/sources.list.d/cuda*",
            "chmod 777 /tmp",
            "apt-get update",
            "apt-get install sudo -y",
            "echo ${NB_USER} ALL=NOPASSWD: ALL >> /etc/sudoers.d/${NB_USER}",
        ]
        self.log_window.loading = True
        stop = False
        for sub_cmd in cmds:
            for lines in decode_lines(exec_cmd.format(cmd=sub_cmd, uid=uid)):
                if len(lines) > 0:
                    self.write_log_lines(lines)
                    if "failed" in lines[-1]:
                        stop = True
            if stop:
                break

        self.log_window.loading = False
        if not stop:
            self.write_log_lines([f"Hack sudo for {uid} done [True]!"])

    @on(Button.Pressed, "#install_sudo")
    def install_sudo_button(self):
        if self.selected_uid is not None:
            self.install_sudo(self.selected_uid)

    @on(Button.Pressed, "#back_button")
    def back_button(self):
        self.log_window.clear()
        self.selected_uid = None
        self.dismiss()

    @on(Button.Pressed, "#exit_button")
    def exit_button(self):
        self.parent.exit()
