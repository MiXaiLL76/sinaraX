import json
import os
from pathlib import Path

from textual import work

from .utils import (
    FilteredConfigTree,
    decode_lines,
    generate_from_screen,
    load_from_file,
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
        for lines in decode_lines(cmd):
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
            self.log_window.write_line(f"[True] Config {selected_file} loaded!")
        else:
            self.log_window.write_line("[False] Config not selected!")
        self.reload_config_dir()

    def get_cfg_button(self):
        self.log_window.clear()
        result = self.generate_config()
        if result:
            self.write_log_lines(json.dumps(self.config_dict, indent=4))

    def save_cfg_button(self):
        self.save_cfg()
