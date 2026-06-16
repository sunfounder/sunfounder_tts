"""TTS example: OpenAI TTS — cloud neural TTS.

Requires an OpenAI API key. Set it before running::

    export OPENAI_API_KEY="sk-..."

Supports multiple voices: alloy, ash, ballad, coral, echo, fable,
nova, onyx, sage, shimmer.
"""

import os
from sunfounder_tts import OpenAI_TTS

api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    api_key = input("Enter your OpenAI API key: ").strip()
    if not api_key:
        print("No API key provided, exiting.")
        exit(1)

tts = OpenAI_TTS(api_key=api_key)
tts.set_voice(tts.Voice.ALLOY)

msg = "Hello! I am OpenAI TTS, a cloud based neural text to speech engine."
print(f"Say: {msg}")
tts.say(msg)

msg = "With instructions, I can change my emotional tone."
instructions = "say it sadly and dramatically"
print(f"Say: {msg}, with instructions: '{instructions}'")
tts.say(msg, instructions=instructions)
