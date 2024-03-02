from textual import on
from textual import events
from textual import work
from textual.app import App
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Checkbox, TextArea, RadioButton, DirectoryTree, Static, Input, RadioSet, Collapsible
from textual.containers import Horizontal, Vertical, ScrollableContainer 
from pathlib import Path
import json
from subprocess import STDOUT, PIPE, Popen, run, CalledProcessError

from typing import Iterable

class FilteredDirectoryTree(DirectoryTree):
    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        return [path for path in paths if (path.is_dir() and (not path.name.startswith(".")))]
    
class CreateServerScreen(ModalScreen):
    CSS_PATH = "style.css"
    config_dict = {}

    def compose(self):
        with ScrollableContainer():
            yield Label("Create server")
            with Collapsible(title="Optional config", id="config"):
                with Horizontal():
                    with Vertical():
                        with Collapsible(title="Sinara server container name"):
                            yield Input(value="jovyan-single-use", name="instanceName")
                        
                        with Collapsible(title="Run Mode"):
                            yield Static("Quick - work, data, tmp will be mounted inside docker volumes")
                            yield Static("Basic - work, data, tmp will be mounted from host folders")
                            
                            with RadioSet(name="runMode"):
                                yield RadioButton("Quick", value=True)
                                yield RadioButton("Basic")

                        with Collapsible(title="Memory"):
                            yield Static("Amount of memory requested for server container")
                            yield Input(value="4g", name="memRequest")
                        
                            yield Static("Maximum amount of memory for server container")
                            yield Input(value="8g", name="memLimit")

                            yield Static("Maximum amount of shared memory for server container")
                            yield Input(value="512m", name="shm_size")
                        
                        with Collapsible(title="Cpu"):
                            yield Static(" Number of CPU cores to use for server container")
                            yield Input(value="4", type="number", name="cpuLimit")
                        
                        with Collapsible(title="Folders Path (only used in basic mode)"):
                            with Collapsible(title="Path to data fodler on host"):
                                yield FilteredDirectoryTree(Path().home().as_posix(), id="jovyanDataPath", name="jovyanDataPath")
                            with Collapsible(title="Path to work fodler on host"):
                                yield FilteredDirectoryTree(Path().home().as_posix(), id="jovyanWorkPath", name="jovyanWorkPath")
                            with Collapsible(title="Path to tmp fodler on host"):
                                yield FilteredDirectoryTree(Path().home().as_posix(), id="jovyanTmpPath", name="jovyanTmpPath")
                            
                    with Vertical():
                        with Collapsible(title="Infrastructure name to use"):
                            yield Input(value="local_filesystem", name="infraName")
                        
                        with Collapsible(title="Server config"):
                            yield Checkbox("Create Folders", value=True, name="createFolders")
                            yield Checkbox("Gpu Enabled", value=True, name="gpuEnabled")
                            yield Checkbox("Run server without password protection", value=False, name="insecure")
                            yield Checkbox("Use expermiental server images", value=False, name="experimental")
                        
                        with Collapsible(title="Server platform"):
                            yield Static("Host where the server is run")
                            
                            with RadioSet(name="platform"):
                                yield RadioButton("Desktop", value=True)
                                yield RadioButton("Remote VM")
            yield Static()   
            with RadioSet(name="sinara_image_num"):
                yield RadioButton("Sinara for CV", value=True)
                yield RadioButton("Sinara for ML")
            
            with Horizontal():
                yield Button("Create!", id="server_button",  variant="success")
                yield Button("Remove!", id="server_remove_button",  variant="error")
                yield Button("HELP", id="help_button", variant="primary")
                yield Button("Get config", id="cfg_button",  variant="success")

            with Horizontal():
                yield Button("Start!", id="server_start_button",  variant="success")
                yield Button("Stop!", id="server_stop_button",  variant="warning")

            with Horizontal():
                yield Button("< Back", id="back_button", classes="back_button", variant="primary")
                yield Button("Exit", id="exit_button", classes="exit_button", variant="error")

            self.static_widget : TextArea = TextArea(disabled=True, id="output_text_area")
            yield self.static_widget
      
    @on(DirectoryTree.DirectorySelected, "#jovyanDataPath")
    def jovyanDataPath_record(
        self, event: DirectoryTree.DirectorySelected
    ) -> None:
        self.config_dict['jovyanDataPath'] = event.path.as_posix()
    
    @on(DirectoryTree.DirectorySelected, "#jovyanWorkPath")
    def jovyanWorkPath_record(
        self, event: DirectoryTree.DirectorySelected
    ) -> None:
        self.config_dict['jovyanWorkPath'] = event.path.as_posix()
    
    @on(DirectoryTree.DirectorySelected, "#jovyanTmpPath")
    def jovyanTmpPath_record(
        self, event: DirectoryTree.DirectorySelected
    ) -> None:
        self.config_dict['jovyanTmpPath'] = event.path.as_posix()
    

    @work(thread=True)
    def generate_config(self):
        for child in self.walk_children():
            if type(child) is Collapsible:
                child.collapsed = True
            
            if child.name is not None:
                if type(child) is RadioSet:
                    self.config_dict[child.name] = child._selected
                elif type(child) is FilteredDirectoryTree:
                    pass
                else:
                    self.config_dict[child.name] = child.value
        
        if self.config_dict.get('runMode') is not None:
            self.config_dict['runMode'] = {
                0 : "q",
                1 : "b",
            }.get(self.config_dict['runMode'])
        
        try:
            if self.config_dict.get('runMode', '') == "b":
                assert len(self.config_dict['jovyanDataPath']) > 0, "jovyanDataPath empty!"
                assert len(self.config_dict['jovyanWorkPath']) > 0, "jovyanWorkPath empty!"
                assert len(self.config_dict['jovyanTmpPath']) > 0, "jovyanTmpPath empty!"
        except AssertionError as e:
            self.static_widget.text = "No path specified for:\n" + str(e)
            return
        except KeyError as e:
            self.static_widget.text = "No path specified for:\n" + str(e)
            return
        
        if self.config_dict.get('sinara_image_num') is not None:
            self.config_dict['sinara_image_num'] = {
                0 : "2",
                1 : "1",
            }.get(self.config_dict['sinara_image_num'])
        
        if self.config_dict.get('platform') is not None:
            self.config_dict['platform'] = {
                0 : "desktop",
                1 : "remote_vm",
            }.get(self.config_dict['platform'])
        
        
        self.config_dict = {key : val for key, val in self.config_dict.items() if (val is not None) and len(str(val)) > 0}

        if self.config_dict.get('createFolders') is not None:
            self.config_dict["createFolders"] = "y" if self.config_dict["createFolders"] else "n"
        
        if self.config_dict.get('gpuEnabled') is not None:
            self.config_dict["gpuEnabled"] = "y" if self.config_dict["gpuEnabled"] else "n"
        
        if self.config_dict.get('experimental') is not None:
            if self.config_dict["experimental"]:
                self.config_dict["experimental"] = ""
            else:
                del self.config_dict["experimental"]
        
        if self.config_dict.get('insecure') is not None:
            if self.config_dict["insecure"]:
                self.config_dict["insecure"] = ""
            else:
                del self.config_dict["insecure"]
        
        self.static_widget.text = json.dumps(self.config_dict, indent=4)
    
    @work(thread=True)
    def create_server_cmd(self):
        cmd = "sinara server create --verbose "
        for key, val in self.config_dict.items():
            val = str(val).replace(" ", "\ ")
            cmd += f"--{key} {val} "
        self.static_widget.text = cmd

        lines = [""]
        with Popen(cmd, shell=True, stdout=PIPE, stdin=PIPE, stderr=PIPE, cwd=None) as child_process:
            for line in child_process.stdout:
                decoded_line = line.decode("utf-8")
                
                if "choose a Sinara" in decoded_line:
                    child_process.stdin.write(self.config_dict['sinara_image_num'].encode())
                    lines.append(self.config_dict['sinara_image_num'])
                
                if "\r" in decoded_line:
                    lines[-1] = decoded_line
                else:
                    lines.append(decoded_line)
                
                self.static_widget.text = "".join(lines)

            child_process.communicate()
            
            if child_process.returncode != 0:
                self.static_widget.text += "SINARA Server Create is failed!"
            else:
                self.static_widget.text += "SINARA Server Create done!"
            
    @work(thread=True)
    def start_cmd(self, cmd : str):
        self.static_widget.text = ""
        with Popen(cmd, shell=True, stdout=PIPE, stderr=STDOUT, cwd=None) as child_process:
            for line in child_process.stdout:
                decoded_line = line.decode("utf-8")
                self.static_widget.text += decoded_line
            child_process.communicate()
            
            if child_process.returncode != 0:
                self.static_widget.text += "SINARA Server failed!"

    
    @on(Button.Pressed, "#server_button")
    def server_button(self):
        self.generate_config()
        self.create_server_cmd()

    @on(Button.Pressed, "#cfg_button")
    def cfg_button(self):
        self.generate_config()
    
    @on(Button.Pressed, "#server_remove_button")
    def server_remove_button(self):
        self.start_cmd("sinara server remove")

    @on(Button.Pressed, "#server_stop_button")
    def server_stop_button(self):
        self.start_cmd("sinara server stop")

    @on(Button.Pressed, "#server_start_button")
    def server_start_button(self):
        self.start_cmd("sinara server start")

    @on(Button.Pressed, "#help_button")
    def help_button(self):
        self.start_cmd("sinara server create -h")

    @on(Button.Pressed, "#back_button")
    def back_button(self):
        self.dismiss()

    @on(Button.Pressed, "#exit_button")
    def exit_button(self):
        self.parent.exit()

class SinaraX(App):
    CSS_PATH = "style.css"

    def compose(self):
        yield Label("SinaraML TUI by MiXaiLL76")
        # yield Static("SinaraML TUI by MiXaiLL76", classes="header")
        yield Horizontal(
            Button("SERVER", id="create_server_button", variant="primary"),
            Button("Exit", id="exit_button", classes="exit_button", variant="warning"),
        )
        
    @on(Button.Pressed, "#create_server_button")
    def create_server_button(self):
        self.push_screen(CreateServerScreen())

    @on(Button.Pressed, "#exit_button")
    def exit_button(self):
        self.exit()
    
SinaraX().run()