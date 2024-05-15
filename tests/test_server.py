import unittest
import logging
from sinaraX.screens.main import SinaraX
from sinaraX.screens.server import ServerScreen
from textual.worker import Worker, WorkerState
from sinaraX.screens.utils import start_cmd

class SinaraX_Server_Test(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.instanceName = 'sinaraX-test'

    async def open_server_screen(self, pilot) -> ServerScreen:
        if type(pilot.app.screen) is ServerScreen:
            return
        
        await pilot.press("s")

        assert type(pilot.app.screen) is ServerScreen

        server_screen : ServerScreen = pilot.app.screen

        for child in server_screen.walk_children():
            if child.name == "instanceName":
                child.value = self.instanceName
        
        assert server_screen.generate_config()
        assert "instanceName" in server_screen.config_dict
        assert server_screen.config_dict['instanceName'] == self.instanceName
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
    
    def get_docker_error(self, status : str = None):
        _status = ""
        if status is not None:
            _status = f"--filter status={status}"
        
        result = True
        for line in start_cmd(f'docker ps -a --filter name="{self.instanceName}" {_status}'):
            if self.instanceName in line:
                result = "failed!" in line
        return not result

    async def test_server(self):
        async with SinaraX().run_test() as pilot:
            server_screen = await self.open_server_screen(pilot)

            server_screen.server_stop_button()
            await self.wait_workers(pilot)

            server_screen.server_remove_button()
            await self.wait_workers(pilot)

            server_screen.server_create_button()
            await self.wait_workers(pilot)

            assert self.get_docker_error("created"), f"server create error \n {server_screen.log_window.lines=}"
            
            server_screen.server_start_button()
            await self.wait_workers(pilot)

            assert self.get_docker_error("running"), f"server start error \n {server_screen.log_window.lines=}"

            server_screen.server_stop_button()
            await self.wait_workers(pilot)

            assert self.get_docker_error("exited"), f"server stop error \n {server_screen.log_window.lines=}"
            
            server_screen.server_remove_button()
            await self.wait_workers(pilot)

            assert not self.get_docker_error(), f"server remove error \n {server_screen.log_window.lines=}"

if __name__ == '__main__':
    unittest.TestLoader.sortTestMethodsUsing = None
    unittest.main()