from textual.widgets import Collapsible, RadioSet


def remap_radio_set(_dict: dict, key: str, remap_dict: dict):
    if _dict.get(key) is not None:
        _dict[key] = remap_dict.get(_dict[key])


def remap_checkbox(_dict: dict, key: str, yes: str, no: str):
    if _dict.get(key) is not None:
        _dict[key] = yes if _dict[key] else no


def generate_from_screen(screen):
    for child in screen.walk_children():
        if type(child) is Collapsible:
            child.collapsed = True

        if child.name is not None:
            if type(child) is RadioSet:
                screen.config_dict[child.name] = child._selected
            else:
                screen.config_dict[child.name] = child.value

    remap_radio_set(screen.config_dict, "runMode", {0: "q", 1: "b"})
    remap_radio_set(screen.config_dict, "sinara_image_num", {0: "2", 1: "1"})
    remap_radio_set(
        screen.config_dict, "platform", {0: "desktop", 1: "remote_vm"}
    )
    remap_checkbox(screen.config_dict, "createFolders", "y", "n")
    remap_checkbox(screen.config_dict, "gpuEnabled", "y", "n")
    remap_checkbox(screen.config_dict, "experimental", " ", None)
    remap_checkbox(screen.config_dict, "insecure", " ", None)

    try:
        if screen.config_dict.get("runMode", "") == "b":
            for _key in ["jovyanDataPath", "jovyanWorkPath", "jovyanTmpPath"]:
                assert (
                    len(screen.config_dict.get(_key, "")) > 0
                ), f"{_key} empty!"
    except AssertionError as e:
        screen.static_widget.text = "No path specified for:\n" + str(e)
        return False

    screen.config_dict = {
        key: val
        for key, val in screen.config_dict.items()
        if (val is not None) and len(str(val)) > 0
    }

    sinara_images = [
        ["buslovaev/sinara-notebook", "buslovaev/sinara-cv"],
        ["buslovaev/sinara-notebook-exp", "buslovaev/sinara-cv-exp"],
    ]

    image_type_id = int(screen.config_dict.get("experimental") is not None)
    image = sinara_images[image_type_id][
        int(screen.config_dict.get("sinara_image_num")) - 1
    ]
    screen.config_dict["image"] = image
    del screen.config_dict["sinara_image_num"]

    return True
