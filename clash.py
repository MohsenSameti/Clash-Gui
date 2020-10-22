import subprocess
from threading import Thread
import psutil


def is_clash_running():
    return "clash" in (p.name() for p in psutil.process_iter())


# TODO: where to find clash?
class ClashMediator:

    def __init__(self):
        self._process: subprocess.Popen = None

    def start(self, kill_if_is_running: bool = True, output_callback=None, end_callback=None):
        if kill_if_is_running and self._process:
            self.kill()

        t = Thread(target=self.create_process, name="clash-thread", args=(output_callback, end_callback,))
        t.start()

    def create_process(self, output_callback=None, end_callback=None):
        self._process = subprocess.Popen(
            args=["clash"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            universal_newlines=True
        )

        while True:
            output = self._process.stdout.readline().strip()
            print(output)
            output_callback(output)

            return_code = self._process.poll()
            if return_code is not None:
                print('RETURN CODE', return_code)
                output_callback("returned with code {}".format(return_code))
                # Process has finished, read rest of the output
                for output in self._process.stdout.readlines():
                    output_callback(output)
                end_callback(return_code)
                break

    def kill(self) -> bool:
        if self._process:
            self._process.kill()
            return True
        return False
