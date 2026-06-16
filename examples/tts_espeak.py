"""TTS example: Espeak — compact offline synthesizer.

Requires: ``espeak`` system package.

Voice is robotic but fast and works fully offline.
"""

from sunfounder_tts import Espeak

tts = Espeak()
# Amp: 0-200, default 100
tts.set_amp(100)
# Speed: 80-260, default 175
tts.set_speed(150)
# Gap: 0-200, default 5
tts.set_gap(3)
# Pitch: 0-99, default 50
tts.set_pitch(50)

tts.say("Hello! I am espeak.")
