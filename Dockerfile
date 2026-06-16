FROM ghcr.io/arduino/app-bricks/python-apps-base:0.10.1
USER root

# System deps: espeak (Espeak engine), sox + libsox-fmt-mp3 (MP3→WAV for EdgeTTS)
RUN apt-get update && apt-get install -y -f && apt-get install -y --no-install-recommends \
    espeak sox libsox-fmt-mp3 \
    && rm -rf /var/lib/apt/lists/*

# Install all three libraries as proper packages.
# TTS requires sunfounder_stt (shared base) and robot_shield (shared utils).
RUN pip install --no-cache-dir \
    git+https://github.com/suxiaofang2711/robot_shield.git@main \
    "sunfounder-stt[all] @ git+https://github.com/suxiaofang2711/sunfounder_stt.git@main" \
    git+https://github.com/suxiaofang2711/sunfounder_tts.git@main

RUN mkdir -p /app/.cache && chown 1000:1000 /app/.cache
USER 1000

ENTRYPOINT ["/bin/sleep"]
CMD ["infinity"]
