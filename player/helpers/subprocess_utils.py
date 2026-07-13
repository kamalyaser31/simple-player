import subprocess


def stop_process(process, terminate_timeout=0.5, kill_timeout=0.5):
    """Stop a child process and release its pipe handles."""
    if process is None:
        return
    try:
        if process.poll() is None:
            process.terminate()
            _wait_or_kill(process, terminate_timeout, kill_timeout)
        else:
            process.wait(timeout=0)
    except (OSError, subprocess.SubprocessError):
        _kill_and_wait(process, kill_timeout)
    finally:
        _close_pipes(process)


def _wait_or_kill(process, terminate_timeout, kill_timeout):
    try:
        process.wait(timeout=terminate_timeout)
    except subprocess.TimeoutExpired:
        _kill_and_wait(process, kill_timeout)


def _kill_and_wait(process, timeout):
    try:
        process.kill()
    except OSError:
        pass
    try:
        process.wait(timeout=timeout)
    except (OSError, subprocess.SubprocessError):
        pass


def _close_pipes(process):
    for name in ("stdin", "stdout", "stderr"):
        pipe = getattr(process, name, None)
        if pipe is None:
            continue
        try:
            pipe.close()
        except OSError:
            pass
