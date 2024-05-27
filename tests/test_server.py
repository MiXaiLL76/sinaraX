import asyncio
import logging
import os
import shutil
import unittest

from parameterized import parameterized
from textual.worker import Worker, WorkerState

from sinaraX.screens.main import SinaraX
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


class SinaraX_Server_Test_Quick(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.instanceName = "sinaraX-test"
        self.jovyanRootPath = "/tmp/sinara_data"

    def tearDown(self) -> None:
        if os.path.isdir(self.jovyanRootPath):
            shutil.rmtree(self.jovyanRootPath)
        return super().tearDown()

    def print_log(self, screen):
        log_split_line = "-" * 50 + " LOG " + "-" * 50

        if "failed" in "".join(screen.log_window.lines):
            _log = logging.error
        else:
            _log = logging.debug

        _log(log_split_line)

        for line in screen.log_window.lines:
            _log(f"{line}")
        _log(log_split_line + "\n")

    @parameterized.expand(
        [
            [SinaraImageType.CV, SinaraRunMode.Quick],
            [SinaraImageType.CV, SinaraRunMode.Basic],
        ]
    )
    async def test_server(
        self,
        sinara_image_num: SinaraImageType,
        runMode: SinaraRunMode,
    ):
        async with SinaraX().run_test() as pilot:
            server_screen = await open_server_screen(
                pilot,
                self.instanceName,
                self.jovyanRootPath,
                sinara_image_num,
                runMode,
            )

            server_screen.server_stop_button()
            await wait_workers(pilot)

            server_screen.server_remove_button()
            await wait_workers(pilot)

            # Create server
            server_screen.server_create_button()
            await wait_workers(pilot)
            self.print_log(server_screen)
            assert await get_docker_error(
                self.instanceName, "created"
            ), "server create error"

            # Start server
            server_screen.server_start_button()
            await wait_workers(pilot)
            self.print_log(server_screen)
            assert await get_docker_error(
                self.instanceName, "running"
            ), "server start error"

            # Stop server
            server_screen.server_stop_button()
            await wait_workers(pilot)
            self.print_log(server_screen)
            assert await get_docker_error(
                self.instanceName, "exited"
            ), "server stop error"

            # Remove server
            server_screen.server_remove_button()
            await wait_workers(pilot)
            self.print_log(server_screen)
            assert not await get_docker_error(
                self.instanceName
            ), "server remove error"

            await pilot.exit(0)


if __name__ == "__main__":
    unittest.TestLoader.sortTestMethodsUsing = None
    unittest.main()
