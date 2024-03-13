import getpass
import importlib.metadata
import json
import platform

import requests
from sinaraml.server import SinaraServer

from .process import start_cmd


def check_docker():
    check_docker_cmd = "docker info -f json"
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


def get_sinara_servers():
    docker_stats = check_docker()
    containers: list[dict] = []
    if docker_stats["ok"]:
        cmd = "docker ps -a --filter 'label=sinaraml.platform' --format json"

        for line in start_cmd(cmd):
            try:
                decoded_line = json.loads(line)
            except json.decoder.JSONDecodeError:
                continue

            ports = decoded_line.get("Ports", "-,-").split(",")
            ports = [
                port.replace("->8888/tcp", "").split(":")[1]
                for port in ports
                if "->8888/tcp" in port
            ]

            ports = [port for port in ports if len(port.strip()) > 0]

            if len(ports) == 0:
                port = 8888
            else:
                port = int(ports[-1])

            image = decoded_line.get("Image", "no image")
            containers.append(
                {
                    "id": decoded_line.get("ID"),
                    "instanceName": decoded_line.get("Names", "no name"),
                    "port": port,
                    "image": "cv" if "cv" in image else "ml",
                    "exp": "exp" in image,
                }
            )

    label_row = ["id", "instanceName", "port", "image", "exp"]
    rows = []
    for row in containers:
        for index in list(row):
            if index not in label_row:
                label_row.append(index)
        rows.append(list(row.values()))

    return [label_row] + rows


def get_instanse_token(instanceName, host_port):
    url = SinaraServer.get_server_url(instanceName)
    token = SinaraServer.get_server_token(url)
    token_str = f"?token={token}" if token else ""
    protocol = SinaraServer.get_server_protocol(url)

    platform = SinaraServer.get_server_platform(instanceName)
    server_ip = SinaraServer.get_server_ip(platform)
    server_url = f"{protocol}://{server_ip}:{host_port}/{token_str}"
    return server_url


def check_last_version(name: str):
    try:
        local_version = (name + "-" + importlib.metadata.version(name)).lower()

        url = f"https://pypi.org/simple/{name}/"
        resp = requests.get(url)
        if resp.status_code == 200:
            text = resp.text.lower()
            lines = text.split("\n")
            lines = [line for line in lines if ".tar.gz" in line]
            version_idx = -1
            for idx, line in enumerate(lines):
                start_idx = line.find(">") + 1
                if start_idx == -1:
                    continue

                end_idx = line.find(".tar.gz", start_idx)

                lines[idx] = line[start_idx:end_idx].lower()
                if local_version == lines[idx]:
                    version_idx = idx

            if version_idx < idx:
                return False, f"Available new! [{lines[idx]}]"
        else:
            return False, "Pypi not available from this env!"
    except UnboundLocalError:
        return False, "UnboundLocalError!"
    except ImportError:
        return False, "ImportError!"

    return True, "Latest!"


if __name__ == "__main__":
    get_sinara_servers()
