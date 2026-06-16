"""sunfounder_tts — Text-to-Speech brick.

Provides offline and online TTS engines:

- ``Espeak``     — compact offline synthesizer (fast, robotic)
- ``OpenAI_TTS`` — cloud TTS via OpenAI API
- ``EdgeTTS``    — free cloud TTS via Microsoft Edge (100+ voices)

Usage::

    from sunfounder_tts import Espeak
    tts = Espeak()
    tts.say("Hello world")
"""

from ._version import __version__
from .edge_tts import EdgeTTS
from .espeak import Espeak
from .openai_tts import OpenAI_TTS

TTS = EdgeTTS

__all__ = ["TTS", "Espeak", "OpenAI_TTS", "EdgeTTS", "__version__"]