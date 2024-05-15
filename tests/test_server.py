import enum
import logging
import os
import shutil
import unittest

from textual.worker import Worker, WorkerState

from sinaraX.screens.main import SinaraX
from sinaraX.screens.server import ServerScreen
from sinaraX.screens.utils import start_cmd

logging.basicConfig(level=logging.DEBUG)


class SinaraImageType(enum.Enum):
    CV = 0
    ML = 1


class SinaraRunMode(enum.Enum):
    Quick = 0
    Basic = 1


class SinaraX_Server_Test_Quick(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.instanceName = "sinaraX-test"
        self.sinara_image_num = SinaraImageType.CV
        self.runMode = SinaraRunMode.Quick
        self.jovyanRootPath = "/tmp/sinara_data"

    def tearDown(self) -> None:
        if os.path.isdir(self.jovyanRootPath):
            shutil.rmtree(self.jovyanRootPath)
        return super().tearDown()

    async def open_server_screen(self, pilot) -> ServerScreen:
        if type(pilot.app.screen) is ServerScreen:
            return

        await pilot.press("s")

        assert type(pilot.app.screen) is ServerScreen

        server_screen: ServerScreen = pilot.app.screen

        for child in server_screen.walk_children():
            if child.name == "instanceName":
                child.value = self.instanceName

            if child.name == "jovyanRootPath":
                child.value = self.jovyanRootPath

            if child.name == "sinara_image_num":
                child._selected = self.sinara_image_num.value
                child.action_toggle_button()

            if child.name == "runMode":
                child._selected = self.runMode.value
                child.action_toggle_button()

        assert server_screen.generate_config()
        assert "instanceName" in server_screen.config_dict
        assert server_screen.config_dict["instanceName"] == self.instanceName
        return server_screen

    async def get_non_loader_worker(self, pilot) -> list[Worker]:
        workers = []
        for worker in pilot.app.workers._workers:
            if worker.name != "_loader":
                if worker.state == WorkerState.RUNNING:
                    workers.append(worker)
        return workers

    async def wait_workers(self, pilot):
        workers = await self.get_non_loader_worker(pilot)
        for worker in workers:
            await worker.wait()

    def get_docker_error(self, status: str = None):
        _status = ""
        if status is not None:
            _status = f"--filter status={status}"

        result = True
        for line in start_cmd(
            f'docker ps -a --filter name="{self.instanceName}" {_status}'
        ):
            if self.instanceName in line:
                result = "failed!" in line
        return not result

    def print_log(self, screen):
        log_split_line = "-" * 50 + " LOG " + "-" * 50
        logging.info(log_split_line)
        for line in screen.log_window.lines:
            logging.info(f"{line}")
        logging.info(log_split_line + "\n")

    async def test_server(self):
        async with SinaraX().run_test() as pilot:
            server_screen = await self.open_server_screen(pilot)

            server_screen.server_stop_button()
            await self.wait_workers(pilot)

            server_screen.server_remove_button()
            await self.wait_workers(pilot)

            # Create server
            server_screen.server_create_button()
            await self.wait_workers(pilot)
            self.print_log(server_screen)
            assert self.get_docker_error("created"), "server create error"

            # Start server
            server_screen.server_start_button()
            await self.wait_workers(pilot)
            self.print_log(server_screen)
            assert self.get_docker_error("running"), "server start error"

            # Stop server
            server_screen.server_stop_button()
            await self.wait_workers(pilot)
            self.print_log(server_screen)
            assert self.get_docker_error("exited"), "server stop error"

            # Remove server
            server_screen.server_remove_button()
            await self.wait_workers(pilot)
            self.print_log(server_screen)
            assert not self.get_docker_error(), "server remove error"


class SinaraX_Server_Test_Basic(SinaraX_Server_Test_Quick):
    def setUp(self):
        self.instanceName = "sinaraX-test"
        self.sinara_image_num = SinaraImageType.CV
        self.runMode = SinaraRunMode.Basic
        self.jovyanRootPath = "/tmp/sinara_data"


if __name__ == "__main__":
    unittest.TestLoader.sortTestMethodsUsing = None
    unittest.main()
