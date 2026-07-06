class PlayerPlaybackMixin:
    def stop(self):
        self._engine.stop()

    def toggle_pause(self):
        return self._engine.toggle_pause()

    def play(self):
        self._engine.play()

    def pause(self):
        self._engine.pause()

    def is_paused(self):
        return self._engine.is_paused()

    def seek(self, seconds):
        self._engine.seek_relative(seconds)

    def seek_absolute(self, seconds):
        self._engine.seek_absolute(seconds)

    def seek_to_end(self):
        duration = self.get_duration()
        if duration is None or duration <= 0:
            return False
        target = max(0.0, duration - 0.2)
        self.seek_absolute(target)
        return True

    def set_volume(self, volume):
        return self._engine.set_volume(volume)

    def change_volume(self, delta):
        return self.set_volume(self.get_volume() + delta)

    def get_volume(self):
        return self._engine.get_volume()

    def set_speed(self, speed):
        return self._engine.set_speed(speed)

    def change_speed(self, delta):
        return self.set_speed(self.get_speed() + delta)

    def get_speed(self):
        return self._engine.get_speed()

    def set_end_behavior(self, behavior):
        behavior = (behavior or "").lower()
        if behavior not in ("advance", "loop", "none"):
            behavior = "advance"
        self._end_behavior = behavior
        self._engine.set_end_behavior(behavior)

    def get_audio_devices(self):
        return self._engine.get_audio_devices()

    def set_audio_device(self, device_name):
        return self._engine.set_audio_device(device_name)

    def get_audio_device(self):
        return self._engine.get_audio_device()

    def set_loop_start(self, seconds):
        return self._engine.set_loop_start(seconds)

    def set_loop_end(self, seconds):
        return self._engine.set_loop_end(seconds)

    def clear_loop(self):
        return self._engine.clear_loop()

    def get_elapsed(self):
        return self._engine.get_elapsed()

    def get_remaining(self):
        remaining = self._engine.get_remaining()
        if remaining is None:
            duration = self.get_duration()
            elapsed = self.get_elapsed()
            if duration is None or elapsed is None:
                return None
            remaining = duration - elapsed
        return remaining

    def get_duration(self):
        return self._engine.get_duration()

    def play_test_speakers_sound(self, path):
        return self._engine.play_test_sound(path)
