import io
from typing import Any, Optional

from pydub import AudioSegment


def load_audiosegment_from_streamlit_audio(audio_file: Any) -> Optional[AudioSegment]:
    """
    Safely load audio returned by st.audio_input across environments.
    Avoids pydub/ffprobe JSON decode errors by reading bytes explicitly
    and passing the detected format to AudioSegment.
    """
    if audio_file is None:
        return None

    try:
        if hasattr(audio_file, "seek"):
            audio_file.seek(0)
        raw_bytes = audio_file.read() if hasattr(audio_file, "read") else None
    except Exception as e:
        print(f"Error reading audio buffer: {e}")
        raw_bytes = None

    if not raw_bytes:
        return None

    mime_type: str = getattr(audio_file, "type", "") or ""
    name: str = getattr(audio_file, "name", "") or ""

    fmt: Optional[str] = None
    if "webm" in mime_type or name.endswith(".webm"):
        fmt = "webm"
    elif "wav" in mime_type or name.endswith(".wav"):
        fmt = "wav"
    elif "mpeg" in mime_type or "mp3" in mime_type or name.endswith(".mp3"):
        fmt = "mp3"
    elif "ogg" in mime_type or name.endswith(".ogg"):
        fmt = "ogg"
    elif (
        "mp4" in mime_type
        or "m4a" in mime_type
        or name.endswith(".m4a")
        or name.endswith(".mp4")
    ):
        fmt = "mp4"

    audio_buffer = io.BytesIO(raw_bytes)

    try:
        if fmt:
            seg = AudioSegment.from_file(audio_buffer, format=fmt)
        else:
            seg = AudioSegment.from_file(audio_buffer)

        return seg.set_channels(1).set_frame_rate(44100)
    except Exception as e:
        print(f"Error converting audio to AudioSegment: {e}")
        return None
