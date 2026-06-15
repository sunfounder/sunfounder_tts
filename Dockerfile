FROM ghcr.io/arduino/app-bricks/python-apps-base:0.10.1
USER root

# System deps: espeak (Espeak engine), sox + libsox-fmt-mp3 (MP3→WAV for EdgeTTS)
RUN apt-get update && apt-get install -y -f && apt-get install -y --no-install-recommends \
    espeak sox libsox-fmt-mp3 \
    && rm -rf /var/lib/apt/lists/*

# Install all three libraries as proper packages.
# TTS requires sunfounder_stt (shared base) and robot_shield (shared utils).
COPY python-libraries/robot_shield /app/python-libraries/robot_shield
COPY python-libraries/sunfounder_stt /app/python-libraries/sunfounder_stt
COPY python-libraries/sunfounder_tts /app/python-libraries/sunfounder_tts
RUN pip install --no-cache-dir \
    /app/python-libraries/robot_shield \
    "/app/python-libraries/sunfounder_stt[all]" \
    /app/python-libraries/sunfounder_tts

RUN mkdir -p /app/.cache && chown 1000:1000 /app/.cache
USER 1000

ENTRYPOINT ["/bin/sleep"]
CMD ["infinity"]
