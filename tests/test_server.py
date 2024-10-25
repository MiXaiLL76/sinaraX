import logging
import os
import shutil
import unittest

from parameterized import parameterized

from sinaraX.screens.main import SinaraX

try:
    from .utils import (
        SinaraImageType,
        SinaraRunMode,
        get_docker_error,
        open_server_screen,
        wait_workers,
    )
except ImportError:
    from utils import (
        SinaraImageType,
        SinaraRunMode,
        get_docker_error,
        open_server_screen,
        wait_workers,
    )

logging.basicConfig(level=logging.WARNING)


class SinaraX_Server_Test_Quick(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.instanceName = "sinaraX-test-Quick"
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
            assert not await get_docker_error(self.instanceName), "server remove error"

            await pilot.exit(0)


if __name__ == "__main__":
    unittest.TestLoader.sortTestMethodsUsing = None
    unittest.main()
