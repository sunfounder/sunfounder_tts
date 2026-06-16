"""PulseAudio playback via libpulse-simple ctypes.

Fallback when ALSA/PyAudio has no output devices (e.g. Qualcomm SoC
where audio routing requires PipeWire).
"""

import ctypes
import os

_LIB = None
try:
    _LIB = ctypes.cdll.LoadLibrary("libpulse-simple.so.0")
except OSError:
    pass

PA_STREAM_PLAYBACK = 1
PA_SAMPLE_S16LE = 3


class _SampleSpec(ctypes.Structure):
    _fields_ = [
        ("format", ctypes.c_int),
        ("rate", ctypes.c_uint32),
        ("channels", ctypes.c_uint8),
    ]


def _setup_signatures():
    lib = _LIB
    lib.pa_simple_new.argtypes = [
        ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int,
        ctypes.c_char_p, ctypes.c_char_p,
        ctypes.POINTER(_SampleSpec), ctypes.c_void_p, ctypes.c_void_p,
        ctypes.POINTER(ctypes.c_int),
    ]
    lib.pa_simple_new.restype = ctypes.c_void_p
    lib.pa_simple_write.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t, ctypes.POINTER(ctypes.c_int)]
    lib.pa_simple_write.restype = ctypes.c_int
    lib.pa_simple_drain.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_int)]
    lib.pa_simple_drain.restype = ctypes.c_int
    lib.pa_simple_free.argtypes = [ctypes.c_void_p]
    lib.pa_simple_free.restype = None
    lib.pa_strerror.argtypes = [ctypes.c_int]
    lib.pa_strerror.restype = ctypes.c_char_p


if _LIB is not None:
    _setup_signatures()


class PulseAudioPlayer:
    """Audio playback via libpulse-simple (PA_STREAM_PLAYBACK).

    Fallback when ALSA/PyAudio has no output devices.

    Args:
        sample_rate: sample rate in Hz (default 22050).
        channels: number of audio channels (default 1).
        gain: volume gain factor (default 1.0).
    """

    def __init__(self, sample_rate=22050, channels=1, gain=1.0):
        if _LIB is None:
            raise ImportError("libpulse-simple.so.0 not available")
        self._rate = sample_rate
        self._channels = channels
        self._gain = gain
        self._handle = None

    def _open(self):
        """Open PulseAudio connection if not already open.

        Raises:
            OSError: if pa_simple_new fails.
        """
        if self._handle is not None:
            return
        spec = _SampleSpec(PA_SAMPLE_S16LE, self._rate, self._channels)
        server = os.environ.get("PULSE_SERVER")
        server_b = server.encode() if server else None
        error = ctypes.c_int(0)
        h = _LIB.pa_simple_new(
            server_b, b"sf-voice", PA_STREAM_PLAYBACK,
            None, b"tts", ctypes.byref(spec), None, None, ctypes.byref(error),
        )
        if not h:
            raise OSError(f"pa_simple_new: {_LIB.pa_strerror(error)}")
        self._handle = h

    def __enter__(self):
        """Context manager entry — opens connection and returns self."""
        self._open()
        return self

    def __exit__(self, *args):
        """Context manager exit — closes connection."""
        self.close()

    def play(self, data: bytes):
        """Play raw PCM audio data.

        Opens the PulseAudio connection on first call. No-op if *data* is empty.

        Args:
            data: Raw S16_LE PCM audio bytes for playback.
        """
        if not data:
            return
        self._open()
        _LIB.pa_simple_write(self._handle, data, len(data), None)

    def flush(self):
        """Drain all pending audio to the hardware (blocking).

        Ensures all buffered data has been written before returning.
        """
        if self._handle:
            _LIB.pa_simple_drain(self._handle, None)

    def close(self):
        """Drain pending audio and close the PulseAudio connection.

        Safe to call multiple times — subsequent calls are no-ops.
        """
        if self._handle:
            try:
                _LIB.pa_simple_drain(self._handle, None)
            except Exception:
                pass
            _LIB.pa_simple_free(self._handle)
            self._handle = None

    def play_file(self, path: str):
        """Play a WAV audio file via PulseAudio.

        Reads the file in 4096-frame chunks, plays each via :meth:`play`,
        then drains.

        Args:
            path: Path to a WAV audio file.
        """
        import wave
        with wave.open(path, "rb") as wf:
            self._rate = wf.getframerate()
            self._open()
            data = wf.readframes(4096)
            while data:
                self.play(data)
                data = wf.readframes(4096)
            self.flush()

    def stop(self):
        """Stop playback by draining any buffered audio to hardware."""
        self.flush()

    @staticmethod
    def is_available():
        """Check if PulseAudio playback is available.

        Returns:
            bool: True if libpulse-simple is loaded and PULSE_SERVER env var is set.
        """
        return _LIB is not None and "PULSE_SERVER" in os.environ
