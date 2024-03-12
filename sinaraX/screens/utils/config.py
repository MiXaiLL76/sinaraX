import argparse
import json
from pathlib import Path
from typing import Iterable

from textual.widgets import Collapsible, DirectoryTree, RadioSet


class AppConfig(argparse.Namespace):
    pass


class FilteredConfigTree(DirectoryTree):
    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        return [
            path
            for path in paths
            if (path.is_file() and path.name.endswith(".json"))
        ]


def remap_radio_set(_dict: dict, key: str, remap_dict: dict):
    if _dict.get(key) is not None:
        _dict[key] = remap_dict.get(_dict[key])


def remap_checkbox(_dict: dict, key: str, remap_dict: dict):
    if _dict.get(key) is not None:
        _dict[key] = remap_dict.get(_dict[key], False)


def remap_config(_dict: dict, _from_screen=True):
    _remap_radio = {
        "runMode": {0: "q", 1: "b"},
        "sinara_image_num": {0: "2", 1: "1"},
        "platform": {0: "desktop", 1: "remote_vm"},
    }

    _remap_checkbox = {
        "createFolders": {True: "y", False: "n"},
        "gpuEnabled": {True: "y", False: "n"},
        "experimental": {True: " ", False: None},
        "insecure": {True: " ", False: None},
    }

    for key, val in _remap_radio.items():
        remap_radio_set(
            _dict, key, val if _from_screen else {v: k for k, v in val.items()}
        )

    for key, val in _remap_checkbox.items():
        remap_checkbox(
            _dict, key, val if _from_screen else {v: k for k, v in val.items()}
        )

    sinara_images = [
        ["buslovaev/sinara-notebook", "buslovaev/sinara-cv"],
        ["buslovaev/sinara-notebook-exp", "buslovaev/sinara-cv-exp"],
    ]
    if _from_screen:
        image_type_id = int(_dict.get("experimental") is not None)
        image = sinara_images[image_type_id][
            int(_dict.get("sinara_image_num")) - 1
        ]
        _dict["image"] = image
        del _dict["sinara_image_num"]
    else:
        image = _dict.get("image")
        if image:
            if "exp" in image:
                _dict["experimental"] = True

            if "cv" in image:
                _dict["sinara_image_num"] = 0
            else:
                _dict["sinara_image_num"] = 1


def load_from_file(screen, file):
    with open(file) as fd:
        config = json.load(fd)

    remap_config(config, False)

    for child in screen.walk_children():
        if config.get(child.name) is not None:
            if type(child) is RadioSet:
                child._selected = config[child.name]
                child.action_toggle()
            else:
                child.value = config[child.name]


def generate_from_screen(screen):
    for child in screen.walk_children():
        if type(child) is Collapsible:
            child.collapsed = True

        if child.name is not None:
            if type(child) is RadioSet:
                screen.config_dict[child.name] = child._selected
            else:
                screen.config_dict[child.name] = child.value

    remap_config(screen.config_dict)

    try:
        if screen.config_dict.get("runMode", "") == "b":
            for _key in ["jovyanRootPath"]:
                assert (
                    len(screen.config_dict.get(_key, "")) > 0
                ), f"{_key} empty!"
    except AssertionError as e:
        screen.write_log_lines("No path specified for:\n" + str(e))
        return False

    screen.config_dict = {
        key: val
        for key, val in screen.config_dict.items()
        if (val is not None) and len(str(val)) > 0
    }

    return True
