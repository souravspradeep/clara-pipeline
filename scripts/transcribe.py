import os
from faster_whisper import WhisperModel

def load_transcript(path):
    """
    If the file is .txt → just read it
    If the file is audio (.mp3, .wav etc.) → transcribe it with Whisper
    """
    ext = os.path.splitext(path)[1].lower()
    
    if ext in [".txt", ".md"]:
        # It's already text, just read it
        with open(path, "r") as f:
            return f.read()
    
    elif ext in [".mp3", ".wav", ".m4a", ".mp4"]:
        # It's audio, convert to text first
        print(f"[TRANSCRIBE] Converting audio to text: {path}")
        model = WhisperModel("base", device="cpu", compute_type="int8")
        segments, info = model.transcribe(path)
        text = " ".join([seg.text.strip() for seg in segments])
        print(f"[TRANSCRIBE] Done. Language detected: {info.language}")
        return text
    
    else:
        raise ValueError(f"Unknown file type: {ext}. Use .txt or .mp3/.wav")