# sunfounder_tts

Text-to-Speech brick — synthesizes audio from text and plays it through the system audio device.

## Engines

| Engine | Quality | Online | Notes |
|---|---|---|---|
| **EdgeTTS** (default) | Natural | Yes | Microsoft Edge cloud TTS, **free**, 100+ voices across 50+ languages. Default voice: `zh-CN-XiaoxiaoNeural`. |
| **Espeak** | Robotic | No | Compact formant synthesizer, zero runtime deps. Supports `-v en-us+f3` for female voice. |
| **OpenAI_TTS** | Best | Yes | OpenAI cloud TTS. Needs `OPENAI_API_KEY`. Voices: alloy, echo, fable, onyx, nova, shimmer. |

The default engine shortcut is `TTS = EdgeTTS`.

## Dependencies

- **EdgeTTS**: `edge-tts` pip package
- **Espeak**: `espeak` system package
- **OpenAI_TTS**: `requests` pip package + internet

## Usage

### EdgeTTS — recommended default (free cloud TTS)

```python
from sunfounder_tts import EdgeTTS

tts = EdgeTTS(voice="zh-CN-XiaoxiaoNeural", gain=0.50)
tts.say("你好，我是UNO")
```

Available voices:

```python
voices = EdgeTTS.available_voices()
# {'zh-CN-XiaoxiaoNeural': 'CN female, natural',
#  'zh-CN-YunxiNeural': 'CN male, professional',
#  'en-US-AriaNeural': 'US female, natural', ...}

tts.set_voice("en-US-JennyNeural")
tts.set_gain(0.75)  # volume factor (1.0 = original)
```

### Espeak — compact offline

```python
from sunfounder_tts import Espeak

tts = Espeak()
tts.set_voice("en-us+f3")   # American English female
tts.set_amp(200)            # volume 0-200, default 100
tts.set_speed(150)          # speed 80-260, default 175
tts.set_pitch(50)           # pitch 0-99, default 50
tts.say("Hello world")
```

### OpenAI TTS — cloud

```python
from sunfounder_tts import OpenAI_TTS

tts = OpenAI_TTS(api_key="sk-...")
tts.set_voice(tts.Voice.ALLOY)
tts.say("Hello from the cloud")
```

## Audio output

Playback uses ALSA LineOut (`hw:0,1`) via PyAudio. The Qualcomm Codec mixer is
configured automatically at container startup
by `setup_audio_output()` in `python-libraries/robot_shield/audio.py`.

EdgeTTS outputs MP3; `AudioPlayer` auto-detects MP3 via magic bytes (`0xFF 0xE0`)
and converts to WAV via `sox` before playback.

System-wide ALSA config is written to `/etc/asound.conf` at image build time:
```
pcm.!default { type plug slave.pcm { type hw card 0 device 1 } }
ctl.!default { type hw card 0 device 1 }
```
