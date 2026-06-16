"""TTS example: EdgeTTS — free cloud TTS via Microsoft Edge.

No API key required. Supports 100+ voices across 50+ languages.
Uses the ``edge-tts`` Python package.

Default voice: en-US-AriaNeural. For Chinese: zh-CN-XiaoxiaoNeural.
"""

from sunfounder_tts import EdgeTTS

# Show available voices
print("Common voices:")
voices = EdgeTTS.available_voices()
for vid, desc in list(voices.items())[:8]:
    print(f"  {vid}: {desc}")

tts = EdgeTTS(voice="en-US-AriaNeural", gain=0.3)

msg = "Hello! I am Edge TTS."
print(f"\nSay: {msg}")
tts.say(msg)


