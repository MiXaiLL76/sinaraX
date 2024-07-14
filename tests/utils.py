import asyncio
import logging

from textual.worker import Worker, WorkerState

from sinaraX.screens.server import ServerScreen
from sinaraX.screens.utils import SinaraImageType, SinaraRunMode, start_cmd

logging.basicConfig(level=logging.WARNING)


async def open_server_screen(
    pilot,
    instanceName: str,
    jovyanRootPath: str,
    sinara_image_num: SinaraImageType,
    runMode: SinaraRunMode,
) -> ServerScreen:
    if type(pilot.app.screen) is ServerScreen:
        return

    await pilot.press("s")

    assert type(pilot.app.screen) is ServerScreen

    server_screen: ServerScreen = pilot.app.screen

    for child in server_screen.walk_children():
        if child.name == "instanceName":
            child.value = instanceName

        if child.name == "jovyanRootPath":
            child.value = jovyanRootPath

        if child.name == "sinara_image_num":
            child._selected = sinara_image_num.value
            child.action_toggle_button()

        if child.name == "runMode":
            child._selected = runMode.value
            child.action_toggle_button()

    assert server_screen.generate_config()
    assert "instanceName" in server_screen.config_dict
    assert server_screen.config_dict["instanceName"] == instanceName
    return server_screen


async def get_non_loader_worker(pilot) -> list[Worker]:
    workers = []
    for worker in pilot.app.workers._workers:
        if worker.name != "_loader":
            if worker.state == WorkerState.RUNNING:
                workers.append(worker)
    logging.debug(f"{workers=}")
    return workers


async def wait_workers(pilot):
    workers = await get_non_loader_worker(pilot)
    for worker in workers:
        await worker.wait()


async def cancel_all_workers(pilot):
    await wait_workers(pilot)
    for worker in pilot.app.workers._workers:
        await worker.cancel()


def _get_docker_error(instanceName: str, status: str = None) -> bool:
    _status = ""
    if status is not None:
        _status = f"--filter status={status}"

    result = True
    for line in start_cmd(
        f'docker ps -a --filter name="{instanceName}" {_status}'
    ):
        if instanceName in line:
            result = "failed!" in line
    return not result


async def get_docker_error(instanceName: str, status: str = None) -> bool:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None, _get_docker_error, instanceName, status
    )
