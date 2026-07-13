import subprocess
import threading
import time
import unittest
from unittest import mock

from helpers.subprocess_utils import stop_process
from youtube.components import CancelFlag, CancelledError
from youtube.download import dl_audio_m4a


class Pipe:
    def __init__(self, calls, name):
        self.calls = calls
        self.name = name

    def close(self):
        self.calls.append(f"close:{self.name}")


class Process:
    def __init__(self):
        self.calls = []
        self.wait_count = 0
        self.stdin = Pipe(self.calls, "stdin")
        self.stdout = Pipe(self.calls, "stdout")
        self.stderr = Pipe(self.calls, "stderr")

    def poll(self):
        return None

    def terminate(self):
        self.calls.append("terminate")

    def wait(self, timeout):
        self.calls.append(f"wait:{timeout}")
        self.wait_count += 1
        if self.wait_count == 1:
            raise subprocess.TimeoutExpired("fake", timeout)
        return 0

    def kill(self):
        self.calls.append("kill")


class BlockingStdout:
    def __init__(self, released):
        self.released = released

    def readline(self):
        self.released.wait(5)
        return ""

    def close(self):
        self.released.set()


class BlockingProcess:
    stdin = None
    stderr = None

    def __init__(self, released):
        self.stdout = BlockingStdout(released)
        self.released = released

    def poll(self):
        return None

    def terminate(self):
        self.released.set()

    def wait(self, timeout):
        return 0

    def kill(self):
        self.released.set()


class SubprocessLifecycleTests(unittest.TestCase):
    def test_stop_escalates_then_closes_all_pipes(self):
        process = Process()

        stop_process(process, terminate_timeout=0.2, kill_timeout=0.3)

        self.assertEqual(
            process.calls,
            [
                "terminate",
                "wait:0.2",
                "kill",
                "wait:0.3",
                "close:stdin",
                "close:stdout",
                "close:stderr",
            ],
        )

    def test_download_cancellation_does_not_wait_for_blocked_stdout(self):
        released = threading.Event()

        cancel = CancelFlag()
        cancel.set()
        started = time.monotonic()
        with mock.patch("youtube.download.yt_path", return_value="yt-dlp.exe"), mock.patch(
            "youtube.download.deno_runtime", return_value=""
        ), mock.patch(
            "youtube.download.os.path.isfile", return_value=True
        ), mock.patch("youtube.download.os.path.isdir", return_value=True), mock.patch(
            "youtube.download.subprocess.Popen", return_value=BlockingProcess(released)
        ):
            with self.assertRaises(CancelledError):
                dl_audio_m4a("https://youtube.test/video", ".", cancel)

        self.assertLess(time.monotonic() - started, 1.0)

    def test_download_inactivity_is_bounded(self):
        released = threading.Event()
        clock = iter((0.0, 61.0))
        with mock.patch("youtube.download.yt_path", return_value="yt-dlp.exe"), mock.patch(
            "youtube.download.deno_runtime", return_value=""
        ), mock.patch(
            "youtube.download.os.path.isfile", return_value=True
        ), mock.patch("youtube.download.os.path.isdir", return_value=True), mock.patch(
            "youtube.download.subprocess.Popen",
            return_value=BlockingProcess(released),
        ), mock.patch(
            "youtube.download.time.monotonic", side_effect=lambda: next(clock)
        ):
            with self.assertRaisesRegex(RuntimeError, "stopped making progress"):
                dl_audio_m4a("https://youtube.test/video", ".", CancelFlag())


if __name__ == "__main__":
    unittest.main()
