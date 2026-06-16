"""Espeak — compact offline TTS engine via the ``espeak`` binary.

Fast, robotic-sounding offline text-to-speech. No network required.

Usage::

    from sunfounder_tts import Espeak
    tts = Espeak(amp=100, speed=160, pitch=50, lang="zh")
    tts.say("你好世界")
"""

from ._utils import is_installed, run_command, check_executable
from ._audio_player import AudioPlayer
from ._base import _Base

class Espeak(_Base):
    """Espeak TTS engine — compact offline synthesizer.

    Fast, robotic-sounding offline TTS. No API key required.

    Args:
        *args: Passed to :class:`sunfounder_tts._base._Base`.
        **kwargs: Passed to :class:`sunfounder_tts._base._Base`.

    Raises:
        Exception: If the ``espeak`` binary is not installed.
    """

    ESPEAK = 'espeak'

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        if not is_installed("espeak"):
            raise Exception("TTS engine: espeak is not installed.")
        self._amp = 100
        self._speed = 175
        self._gap = 5
        self._pitch = 50
        self._lang = 'en-US'

    def tts(self, words: str, file_path: str) -> None:
        """Synthesize text to a WAV file via espeak.

        Args:
            words: Text to synthesize.
            file_path: Output WAV file path.

        Raises:
            Exception: If espeak produces stderr output (indicates failure).
        """
        self.log.debug(f'espeak: [{words}]')
        if not check_executable('espeak'):
            self.log.debug('espeak is busy. Pass')

        cmd = f'espeak -a{self._amp} -s{self._speed} -g{self._gap} -p{self._pitch} "{words}" -w {file_path}'
        _, result = run_command(cmd)
        if len(result) != 0:
            raise Exception(f'tts-espeak:\n\t{result}')
        self.log.debug(f'command: {cmd}')

    def say(self, words: str) -> None:
        """Synthesize text and play it immediately.

        Args:
            words: Text to speak.
        """
        file = './audio_output/espeak.wav'
        self.tts(words, file)
        with AudioPlayer() as player:
            player.play_file(file)

    def set_amp(self, amp: int) -> None:
        """Set amplitude (volume).

        Args:
            amp: Amplitude (0–200, default 100).

        Raises:
            ValueError: If *amp* is out of range.
        """
        if not isinstance(amp, int) or not 0 <= amp <= 200:
            raise ValueError(f'Amp should be in 0 to 200, not "{amp}"')
        self._amp = amp

    def set_speed(self, speed: int) -> None:
        """Set speaking speed in words per minute.

        Args:
            speed: WPM (80–260, default 175).

        Raises:
            ValueError: If *speed* is out of range.
        """
        if not isinstance(speed, int) or not 80 <= speed <= 260:
            raise ValueError(f'speed should be in 80 to 260, not "{speed}"')
        self._speed = speed

    def set_gap(self, gap: int) -> None:
        """Set pause between words.

        Args:
            gap: Gap in milliseconds (0–200, default 5).

        Raises:
            ValueError: If *gap* is out of range.
        """
        if not isinstance(gap, int) or not 0 <= gap <= 200:
            raise ValueError(f'gap should be in 0 to 200, not "{gap}"')
        self._gap = gap

    def set_pitch(self, pitch: int) -> None:
        """Set voice pitch.

        Args:
            pitch: Pitch (0–99, default 50).

        Raises:
            ValueError: If *pitch* is out of range.
        """
        if not isinstance(pitch, int) or not 0 <= pitch <= 99:
            raise ValueError(f'pitch should be in 0 to 99, not "{pitch}"')
        self._pitch = pitch
