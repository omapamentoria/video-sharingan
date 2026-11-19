import sys,json
from faster_whisper import WhisperModel
m=WhisperModel(sys.argv[2],device="cpu",compute_type="int8")
import wave,numpy as np
w=wave.open(sys.argv[1]);a=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)/32768
segs,_=m.transcribe(a,language="pt",vad_filter=True,word_timestamps=True,beam_size=1)
out=[]
with open(sys.argv[3],"w") as f:
    for s in segs:
        out.append({"start":s.start,"end":s.end,"text":s.text,"words":[[w.start,w.end,w.word] for w in (s.words or [])]})
        f.write(f"[{s.start:7.1f}-{s.end:7.1f}] {s.text}\n"); f.flush()
json.dump(out,open(sys.argv[3]+".json","w"),ensure_ascii=False)
