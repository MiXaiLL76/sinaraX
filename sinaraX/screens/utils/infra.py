import getpass
import importlib.metadata
import json
import platform
import re

import requests

from .process import start_cmd


def update_sinara_org():
    cmd = "sinara org update"
    failed = False
    lines = []
    for line in start_cmd(cmd):
        lines.append(line)
        if "failed" in line:
            failed = True

        if "docker: not found" in line:
            failed = True
    return lines, failed


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


def get_server_url(instance):
    url = None
    commands = [
        "jupyter lab list",
        "jupyter server list",
        "jupyter notebook list",
    ]
    for cmd in commands:
        if url:
            continue

        for line in start_cmd(f"docker exec {instance} {cmd}"):
            if url:
                continue

            if any(x in line for x in ["http://", "https://"]):
                m = re.search(r"(http[^\s]+)", line)
                url = m.group(1) if m else None

    return url


def get_server_token(server_url):
    m = re.search(r"token=([a-f0-9-][^\s]+)", server_url)
    return m.group(1) if m else None


def get_server_protocol(server_url):
    m = re.search(r"^(http:|https:)", server_url)
    return str(m.group(1))[:-1] if m else None


def get_instanse_token(instanceName, host_port):
    url = get_server_url(instanceName)

    try:
        token = get_server_token(url)
    except TypeError:
        token = None

    token_str = f"?token={token}" if token else ""

    try:
        protocol = get_server_protocol(url)
    except TypeError:
        protocol = "http"

    server_ip = "localhost"
    server_url = f"{protocol}://{server_ip}:{host_port}/{token_str}"
    return server_url


def check_last_version(name: str):
    try:
        local_version = str(importlib.metadata.version(name)).lower()

        url = f"https://pypi.org/pypi/{name}/json"
        resp = requests.get(url)
        if resp.status_code == 200:
            package_data = resp.json()

            last_version = (
                package_data.get("info", {})
                .get("version", "not found!")
                .lower()
            )

            if last_version != local_version:
                return (
                    False,
                    f"Available new! [{local_version}] < [{last_version}]",
                )
        else:
            return False, "Pypi not available from this env!"
    except UnboundLocalError:
        return False, "UnboundLocalError!"
    except ImportError:
        return False, "ImportError!"

    return True, "Latest!"


if __name__ == "__main__":
    get_sinara_servers()
