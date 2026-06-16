# CLAUDE.md

This file provides guidance to Claude Code when working with the `sunfounder_tts` library.

## Overview

`sunfounder_tts` provides text-to-speech with three engines and a layered audio playback system. Designed for embedded Linux (QCM2290) with PyAudio/ALSA primary and PulseAudio fallback.

```
Text → Engine (EdgeTTS/Espeak/OpenAI) → audio file → AudioPlayer → ALSA/PulseAudio
```

Two-layer volume control: software gain (Python) × hardware DAC (ALSA mixer).

## Public API

Exported from `sunfounder_tts/__init__.py`:

| Symbol | Purpose |
|---|---|
| `TTS` | Alias for `EdgeTTS` (default engine) |
| `EdgeTTS` | Free Microsoft cloud TTS, 66 voices, 20 languages |
| `Espeak` | Offline TTS via espeak binary |
| `OpenAI_TTS` | OpenAI cloud TTS via `gpt-4o-mini-tts` |

## Engine comparison

| Engine | Network | Voices | Output | Key dependency |
|---|---|---|---|---|
| `EdgeTTS` | Required | 66 (20 langs) | MP3 | `edge-tts` package |
| `Espeak` | Offline | N/A (robotic) | WAV | `espeak` binary |
| `OpenAI_TTS` | Required | 10 | WAV | `requests` + API key |

### EdgeTTS (default, `TTS` alias)

```python
from sunfounder_tts import EdgeTTS

tts = EdgeTTS(voice="zh-CN-XiaoxiaoNeural", gain=0.5)
tts.say("你好世界")           # synthesize + play in one call
tts.tts("hello", "/tmp/out.mp3")  # synthesize to file only
tts.set_voice("en-US-AriaNeural")
tts.set_gain(0.3)
voices = EdgeTTS.available_voices()  # dict of {id: description}
```

`tts()` creates a new asyncio event loop internally. `say()` calls `tts()` then plays via `AudioPlayer`. MP3 output is auto-converted to WAV by `AudioPlayer.play_file()` using `sox`.

### Espeak (offline)

```python
from sunfounder_tts import Espeak

tts = Espeak(amp=100, speed=160, gap=5, pitch=50, lang="zh")
tts.say("你好")
```

Parameters: `amp` (0–200), `speed` (80–260 words/min), `gap` (0–200, pause between words in 10ms units), `pitch` (0–99). Uses CLI: `espeak -a{amp} -s{speed} -g{gap} -p{pitch} "{text}" -w {file}`.

### OpenAI_TTS

```python
from sunfounder_tts import OpenAI_TTS

tts = OpenAI_TTS(voice="coral", gain=1.0)
tts.set_api_key("sk-...")
tts.say("Hello")
```

Model: `gpt-4o-mini-tts`. 10 voices. Stream mode: writes each chunk to `AudioPlayer.play()` for real-time output. Output format: WAV.

## AudioPlayer

Internal class in `_audio_player.py` (not in `__init__.py` exports, but used by all engines).

```python
with AudioPlayer(gain=0.5, sample_rate=22050, channels=1) as player:
    player.play(audio_bytes)       # raw PCM
    player.play_file("out.wav")    # WAV or MP3 (auto-converts MP3 via sox)
    player.play_file_async("...")  # non-blocking
```

### Device selection fallback chain

```
PyAudio (ALSA) → PulseAudio (libpulse-simple ctypes) → Error
```

1. Try `pyaudio.PyAudio()` — if `get_device_count() == 0`, fall back
2. Try `PulseAudioPlayer` — requires `PULSE_SERVER` env var
3. Raise `OSError` if both fail

### MP3→WAV conversion

`AudioPlayer.play_file()` detects MP3 via magic bytes (`0xFF 0xE0`) and converts:

```bash
sox input.mp3 output.wav
```

Requires `libsox-fmt-mp3` (installed via project Dockerfile). Conversion failure raises `RuntimeError`.

### Gain application

`_apply_gain()` uses numpy: `array = (array * gain).clip(min, max)`. Maps PyAudio format constants to numpy dtypes (`paInt16 → np.int16`, etc.). Buffering is enabled by default (`enable_buffering=True`, `buffer_size=8192`).

## Internal modules (not exported)

| Module | Purpose |
|---|---|
| `_base.py` | `_Base` — shared `__init__` boilerplate (log, samplerate, etc.) |
| `_audio_player.py` | `AudioPlayer` — PyAudio/PulseAudio playback with gain, buffering, MP3 support |
| `_pulse_audio.py` | `PulseAudioPlayer` — PulseAudio fallback via `libpulse-simple` ctypes |
| `_utils.py` | `redirect_error_2_null()`, `cancel_redirect_error()` — suppress ALSA stderr spam |

## Voice list (EdgeTTS)

66 voices in `VOICES` dict, keyed by short name. Covers: English (US/UK/AU/IN), Chinese (CN/TW/HK), Japanese, Korean, French (FR/CA), German, Spanish (ES/MX), Italian, Portuguese (BR/PT), Russian, Arabic, Hindi, Thai, Vietnamese, Indonesian, Dutch, Polish, Turkish, Swedish, Malay, Filipino.

Default: `zh-CN-XiaoxiaoNeural` (Chinese female, natural).

## Volume architecture

```
Final volume = software gain × hardware DAC
            = EdgeTTS(gain=0.50) × ALSA RX Digital(37/124≈30%)
            ≈ 15%
```

- **Software gain**: Engine-level `gain` parameter, applied via numpy in `AudioPlayer._apply_gain()`
- **Hardware DAC**: `RX_RX0/RX1 Digital=37` (range 0–124), set via `amixer sset` in `robot_shield.setup_audio_output()`

## Dependencies

- **`[project] dependencies`**: `edge-tts>=6.0`, `numpy>=1.24`, `pyaudio>=0.2`, `requests>=2.25`
- **System**: `espeak` binary, `sox` with `libsox-fmt-mp3` (for MP3→WAV), ALSA/PulseAudio
- **No Arduino Bridge dependency** — this library is pure Python + system audio

## Testing

```bash
docker exec uno-q-ai-robot-puls-main-1 python /app/python-libraries/sunfounder_tts/examples/tts_edge.py
docker exec uno-q-ai-robot-puls-main-1 python /app/python-libraries/sunfounder_tts/examples/tts_espeak.py
docker exec uno-q-ai-robot-puls-main-1 python /app/python-libraries/sunfounder_tts/examples/tts_openai.py
```

All engines require audio output hardware (ALSA/PulseAudio). `EdgeTTS.tts()` (file-only) can work without audio hardware.

## Code conventions

- `say()` = synthesize + play (convenience); `tts()` = synthesize to file only
- `AudioPlayer` is a context manager — always use `with AudioPlayer(...) as player:`
- ALSA stderr spam is suppressed via `redirect_error_2_null()` / `cancel_redirect_error()` in `_utils.py`
- Voice lists are class-level constants, not instance attributes
- `_is_mp3()` checks file magic bytes, not extension
- All engines inherit from `_Base` which provides `self.log` (logger) and `self.samplerate`
