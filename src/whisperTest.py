import whisper

model = whisper.load_model("base.en")
result = model.transcribe("../data/downsampledAudio.wav")
print(result["text"])