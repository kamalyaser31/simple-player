import wave


class WavSink:
    def __init__(self, path, channels, rate):
        self._wave = wave.open(path, "wb")
        self._wave.setnchannels(int(channels))
        self._wave.setsampwidth(2)
        self._wave.setframerate(int(rate))

    def write(self, data):
        self._wave.writeframes(data)

    def close(self):
        self._wave.close()


class Mp3Sink:
    def __init__(self, path, channels, rate, bitrate):
        try:
            import lameenc
        except Exception as exc:
            raise RuntimeError("MP3 encoding is unavailable. Install 'lameenc'.") from exc
        self._enc = lameenc.Encoder()
        self._enc.set_bit_rate(int(bitrate))
        self._enc.set_in_sample_rate(int(rate))
        self._enc.set_channels(int(channels))
        self._enc.set_quality(2)
        self._fh = open(path, "wb")

    def write(self, data):
        block = self._enc.encode(data)
        if block:
            self._fh.write(block)

    def close(self):
        tail = self._enc.flush()
        if tail:
            self._fh.write(tail)
        self._fh.close()


def make_sink(fmt, path, channels, rate, bitrate):
    key = str(fmt or "wav").strip().lower()
    if key == "mp3":
        return Mp3Sink(path, channels, rate, bitrate)
    return WavSink(path, channels, rate)
