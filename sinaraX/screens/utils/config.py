import enum
import json
from pathlib import Path
from typing import Iterable

from textual.widgets import DirectoryTree, RadioSet

from .sinara_server_utils import get_memory_size_limit


class SinaraImageType(enum.Enum):
    CV = 0
    ML = 1


class SinaraRunMode(enum.Enum):
    Quick = 0
    Basic = 1


class FilteredConfigTree(DirectoryTree):
    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        return [
            path for path in paths if (path.is_file() and path.name.endswith(".json"))
        ]


def remap_radio_set(_dict: dict, key: str, remap_dict: dict):
    if _dict.get(key) is not None:
        _dict[key] = remap_dict.get(_dict[key])


def remap_checkbox(_dict: dict, key: str, remap_dict: dict):
    if _dict.get(key) is not None:
        _dict[key] = remap_dict.get(_dict[key], False)


def remap_config(_dict: dict, _from_screen=True):
    _remap_radio = {
        "runMode": {
            SinaraRunMode.Quick.value: "q",
            SinaraRunMode.Basic.value: "b",
        },
        "sinara_image_num": {
            SinaraImageType.CV.value: "2",
            SinaraImageType.ML.value: "1",
        },
    }

    _remap_checkbox = {
        "gpuEnabled": {True: "y", False: "n"},
        "experimental": {True: "store_true", False: None},
        "insecure": {True: "store_true", False: None},
    }

    if _dict.get("memLimit"):
        if _from_screen:
            _dict["memLimit"] = int(float(_dict.get("memLimit")) * 1024 * 1024 * 1024)
        else:
            memLimit = str(_dict["memLimit"])
            if "g" in memLimit:
                memLimit = int(memLimit.replace("g", ""))
            elif "m" in memLimit:
                memLimit = float(memLimit.replace("m", "")) / 1024
            elif type(_dict["memLimit"]) is int:
                max_mem = get_memory_size_limit()
                if int(memLimit) > max_mem:
                    memLimit = max_mem

                memLimit = int(memLimit) // 1024 // 1024 // 1024
            else:
                memLimit = None
                del _dict["memLimit"]

            if memLimit is not None:
                _dict["memLimit"] = str(memLimit)

    if _dict.get("cpuLimit"):
        if _from_screen:
            _dict["cpuLimit"] = int(_dict["cpuLimit"])
        else:
            _dict["cpuLimit"] = str(_dict["cpuLimit"])

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
        image = sinara_images[image_type_id][int(_dict.get("sinara_image_num")) - 1]
        _dict["image"] = image
        _dict["serverType"] = "cv" if "cv" in image else "ml"
        del _dict["sinara_image_num"]
    else:
        image = _dict.get("image")
        if image:
            if "exp" in image:
                _dict["experimental"] = True

            if "cv" in image:
                _dict["sinara_image_num"] = SinaraImageType.CV.value
            else:
                _dict["sinara_image_num"] = SinaraImageType.ML.value


def load_from_file(screen, file):
    with open(file) as fd:
        config = json.load(fd)

    remap_config(config, False)

    for child in screen.walk_children():
        if config.get(child.name) is not None:
            if type(child) is RadioSet:
                child._selected = config[child.name]
                child.action_toggle_button()
            else:
                child.value = config[child.name]


def generate_from_screen(screen):
    for child in screen.walk_children():
        if child.name is not None:
            if type(child) is RadioSet:
                screen.config_dict[child.name] = child._selected
            else:
                screen.config_dict[child.name] = child.value

    remap_config(screen.config_dict)

    try:
        if screen.config_dict.get("runMode", "") == "b":
            for _key in ["jovyanRootPath"]:
                assert len(screen.config_dict.get(_key, "")) > 0, f"{_key} empty!"
    except AssertionError as e:
        screen.write_log_lines("No path specified for:\n" + str(e))
        return False

    screen.config_dict = {
        key: val
        for key, val in screen.config_dict.items()
        if (val is not None) and len(str(val)) > 0
    }

    return True
