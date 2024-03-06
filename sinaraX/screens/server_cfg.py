import json
import os
from pathlib import Path

from textual import work

from .utils import (
    FilteredConfigTree,
    generate_from_screen,
    load_from_file,
    start_cmd,
)


class BaseFunctions:
    def write_log_lines(self, lines):
        self.log_window.clear()

        if type(lines) is list:
            self.log_window.write_lines(lines)

        elif type(lines) is str:
            self.log_window.write(lines)

        else:
            self.log_window.write(f"{type(lines)=} not supported!")

        self.app.refresh(layout=True)

    @work(thread=True)
    def cmd(self, cmd: str):
        self.write_log_lines([cmd + "\n"])
        lines = [" "]
        for decoded_line in start_cmd(cmd):
            if len(decoded_line) > 0:
                if lines[-1][-1] == "\r":
                    lines[-1] = decoded_line
                else:
                    lines.append(decoded_line)

            self.write_log_lines([cmd + "\n"] + lines[1:])


class ServerFunctions(BaseFunctions):
    def generate_config(self):
        result = generate_from_screen(self)
        return result

    @work(thread=True)
    def reload_config_dir(self):
        sinaraX_path = Path().home().joinpath(".sinaraX")
        sinaraX_path.mkdir(exist_ok=True)
        self.config_tree.path = sinaraX_path

    @work(thread=True)
    def save_cfg(self):
        result = self.generate_config()
        if result:
            sinaraX_path = Path().home().joinpath(".sinaraX")
            sinaraX_path.mkdir(exist_ok=True)
            config_name = sinaraX_path.joinpath(
                self.config_dict.get("instanceName", "base.") + ".json"
            )
            with open(config_name, "w") as fd:
                json.dump(self.config_dict, fd)

            self.log_window.write_line(f"Config {config_name} saved!")
            self.reload_config_dir()
        else:
            self.log_window.write_line("Config not saved!")

    def select_config(self, event: FilteredConfigTree.FileSelected):
        self.selected_config_path = event.path.as_posix()

    def remove_config_file_button(self):
        selected_file = Path(str(self.selected_config_path))
        if selected_file.is_file():
            os.remove(selected_file.as_posix())
            self.log_window.write_line(f"Config {selected_file} removed!")
        self.reload_config_dir()

    def load_cfg_button(self):
        selected_file = Path(str(self.selected_config_path))
        if selected_file.is_file():
            load_from_file(self, selected_file.as_posix())
            self.log_window.write_line(f"Config {selected_file} loaded!")
        self.reload_config_dir()

    def get_cfg_button(self):
        self.log_window.clear()
        result = self.generate_config()
        if result:
            self.write_log_lines(json.dumps(self.config_dict, indent=4))

    def save_cfg_button(self):
        self.save_cfg()
