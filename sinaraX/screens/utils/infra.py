import getpass
import json
import platform

from .process import start_cmd

check_docker_cmd = "docker info -f json"


def check_docker():
    lines = []
    failed = False
    for line in start_cmd(check_docker_cmd):
        lines.append(line)
        if "failed" in line:
            failed = True

        if "docker: not found" in line:
            failed = True

    result = {
        "ok": not failed,
        "ServerVersion": None,
        "NCPU": None,
        "MemTotal": None,
        "ServerErrors": [],
    }

    if not failed:
        output = "".join(lines)
        start_json = output.find("{")
        end_json = len(output) - output[::-1].find("}")
        if (start_json != -1) and (end_json != -1):
            docker_info = json.loads(output[start_json:end_json])
            result["NCPU"] = docker_info.get("NCPU")
            result["ServerErrors"] = docker_info.get("ServerErrors", [])
            result["ServerVersion"] = docker_info.get("ServerVersion")
            result["MemTotal"] = round(
                int(docker_info.get("MemTotal")) / 1024 / 1024, 2
            )
            for err in result.get("ServerErrors"):
                if "error during connect" in err:
                    result["ok"] = False
    return result


def check_platform():
    _platform = platform.system()
    is_windows = "Windows" in _platform
    result = {
        "ok": not is_windows,
        "platform": _platform,
    }
    return result


def check_docker_group():
    result = {
        "docker_group": False,
        "user_in_group": False,
        "is_unix": False,
        "username": getpass.getuser(),
    }

    try:
        import grp

        docker_group = grp.getgrnam("docker")
        result["docker_group"] = True
        result["is_unix"] = True
        result["user_in_group"] = (
            result["username"] in docker_group.gr_mem
        ) or (result["username"] == "root")
    except ModuleNotFoundError:
        pass
    except KeyError:
        pass

    return result
