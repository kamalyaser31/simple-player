import math
import os
import struct
import threading
import time

from .opts import build_name, ensure_folder
from .sink import make_sink

START_BEEP_FREQ = 880.0
STOP_BEEP_FREQ = 440.0


class RecEngine:
    def __init__(self):
        self._lock = threading.Lock()
        self._running = False
        self._paused = False
        self._stop = threading.Event()
        self._thread = None
        self._stream = None
        self._pa = None
        self._pa_mod = None
        self._sink = None
        self._opts = None
        self._path = ""

    @property
    def is_running(self):
        return bool(self._running)

    @property
    def is_paused(self):
        return bool(self._paused)

    def start(self, opts):
        with self._lock:
            if self._running:
                return {"ok": False, "error": "Recording is already running.", "path": ""}
            try:
                self._pa_mod = _load_pyaudio()
                self._pa = self._pa_mod.PyAudio()
                self._play_beep(freq=START_BEEP_FREQ)
                time.sleep(0.1)
                self._opts = opts
                folder = ensure_folder(opts.folder)
                name = build_name(opts.fmt)
                self._path = os.path.join(folder, name)
                self._sink = make_sink(
                    opts.fmt,
                    self._path,
                    opts.channels,
                    opts.rate,
                    opts.bitrate,
                )
                self._stream = self._pa.open(
                    format=self._pa_mod.paInt16,
                    channels=int(opts.channels),
                    rate=int(opts.rate),
                    input=True,
                    frames_per_buffer=int(opts.chunk),
                )
                self._stop.clear()
                self._paused = False
                self._running = True
                self._thread = threading.Thread(target=self._loop, name="RecorderThread", daemon=True)
                self._thread.start()
                return {"ok": True, "error": "", "path": self._path}
            except Exception as exc:
                self._cleanup_all()
                return {"ok": False, "error": str(exc), "path": ""}

    def pause(self):
        with self._lock:
            if not self._running:
                return {"ok": False, "error": "Recording is not running."}
            self._paused = True
            return {"ok": True, "error": ""}

    def resume(self):
        with self._lock:
            if not self._running:
                return {"ok": False, "error": "Recording is not running."}
            if not self._paused:
                return {"ok": True, "error": ""}
            try:
                self._play_beep(freq=START_BEEP_FREQ)
                time.sleep(0.1)
            except Exception:
                pass
            self._paused = False
            return {"ok": True, "error": ""}

    def stop(self, beep=True):
        with self._lock:
            if not self._running:
                return {"ok": True, "error": "", "path": ""}
            self._running = False
            self._paused = False
            self._stop.set()
            th = self._thread
        if th is not None:
            th.join(timeout=2.0)

        err = ""
        try:
            self._close_input_stream()
        except Exception as exc:
            err = str(exc)

        if beep:
            try:
                self._play_beep(freq=STOP_BEEP_FREQ)
            except Exception:
                pass

        try:
            self._close_finalize()
        except Exception as exc:
            if not err:
                err = str(exc)
        path = self._path
        self._cleanup_all()
        return {"ok": not bool(err), "error": err, "path": path}

    def _loop(self):
        while not self._stop.is_set():
            stream = self._stream
            if stream is None:
                break
            try:
                chunk = stream.read(int(self._opts.chunk), exception_on_overflow=False)
            except Exception:
                break
            if self._paused:
                continue
            sink = self._sink
            if sink is None:
                break
            try:
                sink.write(chunk)
            except Exception:
                break

    def _close_io(self):
        self._close_input_stream()
        self._close_finalize()

    def _close_input_stream(self):
        if self._stream is None:
            return
        try:
            self._stream.stop_stream()
        except Exception:
            pass
        try:
            self._stream.close()
        except Exception:
            pass
        self._stream = None

    def _close_finalize(self):
        if self._sink is not None:
            self._sink.close()
            self._sink = None
        if self._pa is not None:
            try:
                self._pa.terminate()
            except Exception:
                pass
            self._pa = None
            self._pa_mod = None

    def _cleanup_all(self):
        self._close_io()
        self._thread = None
        self._opts = None
        self._path = ""
        self._stop.clear()
        self._paused = False
        self._running = False

    def _play_beep(self, freq=880.0, duration=0.12, amp=0.3):
        pa = self._pa
        pa_mod = self._pa_mod
        if pa is None or pa_mod is None:
            return
        rate = 44100
        count = max(1, int(float(duration) * rate))
        amp = max(0.0, min(1.0, float(amp)))
        frames = bytearray()
        for i in range(count):
            value = int(32767.0 * amp * math.sin((2.0 * math.pi * float(freq) * i) / rate))
            frames.extend(struct.pack("<h", value))
        stream = pa.open(
            format=pa_mod.paInt16,
            channels=1,
            rate=rate,
            output=True,
            frames_per_buffer=1024,
        )
        try:
            stream.write(bytes(frames))
        finally:
            try:
                stream.stop_stream()
            except Exception:
                pass
            try:
                stream.close()
            except Exception:
                pass


def _load_pyaudio():
    try:
        import pyaudio
    except Exception as exc:
        raise RuntimeError("Recording is unavailable. Install 'pyaudio'.") from exc
    return pyaudio
