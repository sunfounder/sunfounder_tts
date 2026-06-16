"""sunfounder_tts — Text-to-Speech brick.

Provides offline and online TTS engines:

- ``Espeak``     — compact offline synthesizer (fast, robotic)
- ``OpenAI_TTS`` — cloud TTS via OpenAI API
- ``EdgeTTS``    — free cloud TTS via Microsoft Edge (100+ voices)

Usage::

    from sunfounder_tts import EdgeTTS, Espeak, OpenAI_TTS

    # EdgeTTS — free cloud TTS, 100+ voices, no API key
    tts = EdgeTTS(voice="zh-CN-XiaoxiaoNeural", gain=0.5)
    tts.say("你好世界")

    # Espeak — compact offline TTS, fast and robotic
    tts = Espeak(amp=100, speed=160, pitch=50, lang="zh")
    tts.say("你好")

    # OpenAI_TTS — cloud TTS via gpt-4o-mini-tts, 10 voices
    tts = OpenAI_TTS(voice="coral", api_key="sk-...", gain=1.5)
    tts.say("Hello world")
"""

from ._version import __version__
from .edge_tts import EdgeTTS
from .espeak import Espeak
from .openai_tts import OpenAI_TTS

TTS = EdgeTTS

__all__ = ["TTS", "Espeak", "OpenAI_TTS", "EdgeTTS", "__version__"]