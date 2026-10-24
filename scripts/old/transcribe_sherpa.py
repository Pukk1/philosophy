"""Транскрипция через Whisper (ONNX, sherpa-onnx). Работает без Hugging Face:
модели берутся из релизов github.com/k2-fsa/sherpa-onnx.

    python transcribe_sherpa.py lecture.wav --models models --out transcripts --name "лекция 1"

Вход: WAV 16 кГц моно (ffmpeg -i in.mp4 -vn -ac 1 -ar 16000 -c:a pcm_s16le out.wav).
Возобновляемый: готовые сегменты копятся в <name>.jsonl, при перезапуске пропускаются.
"""
import argparse
import json
import time
from pathlib import Path

import numpy as np
import sherpa_onnx
import soundfile as sf


def ts(sec: float, sep: str = ",") -> str:
    ms = int(round(sec * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02}{sep}{ms:03}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("wav")
    ap.add_argument("--models", default="models")
    ap.add_argument("--model", default="turbo", help="имя модели sherpa-onnx-whisper-<model>")
    ap.add_argument("--out", default="transcripts")
    ap.add_argument("--name", help="имя выходных файлов (по умолч. имя wav)")
    ap.add_argument("--language", default="ru")
    ap.add_argument("--threads", type=int, default=2)
    ap.add_argument("--precision", choices=["int8", "fp32"], default="int8")
    args = ap.parse_args()
    suffix = ".int8" if args.precision == "int8" else ""

    models = Path(args.models)
    mdir = models / f"sherpa-onnx-whisper-{args.model}"
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    name = args.name or Path(args.wav).stem
    jsonl = out / f"{name}.jsonl"

    done = []
    if jsonl.exists():
        done = [json.loads(l) for l in jsonl.read_text(encoding="utf-8").splitlines() if l.strip()]
    resume_from = done[-1]["end"] if done else 0.0

    samples, sr = sf.read(args.wav, dtype="float32")
    assert sr == 16000, "нужен WAV 16 кГц"
    if samples.ndim > 1:
        samples = samples.mean(axis=1)
    total = len(samples) / sr

    # нарезка на куски <= 29 с по самым тихим местам (Whisper работает окнами 30 с;
    # VAD-нарезка на короткие сегменты давала мусор вида "!!!!")
    hop = sr // 10  # 100 мс
    n = len(samples) // hop
    energy = np.sqrt((samples[: n * hop].reshape(n, hop) ** 2).mean(axis=1))
    cuts, pos = [0], 0
    while pos + 29 * 10 < n:
        lo, hi = pos + 22 * 10, pos + 29 * 10
        pos = lo + int(np.argmin(energy[lo:hi]))
        cuts.append(pos)
    cuts.append(n + 1)
    chunks = [(cuts[i] * hop, min(cuts[i + 1] * hop, len(samples))) for i in range(len(cuts) - 1)]

    rec = sherpa_onnx.OfflineRecognizer.from_whisper(
        encoder=str(mdir / f"{args.model}-encoder{suffix}.onnx"),
        decoder=str(mdir / f"{args.model}-decoder{suffix}.onnx"),
        tokens=str(next(mdir.glob("*tokens.txt"))),
        language=args.language,
        task="transcribe",
        num_threads=args.threads,
    )

    t0 = time.time()
    with open(jsonl, "a", encoding="utf-8") as fout:
        for a, b in chunks:
            start, end = a / sr, b / sr
            if end <= resume_from + 1e-3:
                continue
            x = samples[a:b]
            if np.sqrt((x ** 2).mean()) < 1e-3:  # тишина
                continue
            st = rec.create_stream()
            st.accept_waveform(sr, x)
            rec.decode_stream(st)
            text = st.result.text.strip()
            if text:
                fout.write(json.dumps({"start": round(start, 2), "end": round(end, 2), "text": text},
                                      ensure_ascii=False) + "\n")
                fout.flush()
            el = time.time() - t0
            print(f"{end / total:6.1%} [{ts(end, '.')[:8]}/{ts(total, '.')[:8]}] {el / 60:5.1f} мин | {text[:70]}",
                  flush=True)

    # финальная сборка txt / srt из jsonl
    segs = [json.loads(l) for l in jsonl.read_text(encoding="utf-8").splitlines() if l.strip()]
    with open(out / f"{name}.srt", "w", encoding="utf-8") as f:
        for i, s in enumerate(segs, 1):
            f.write(f"{i}\n{ts(s['start'])} --> {ts(s['end'])}\n{s['text']}\n\n")
    # txt: абзацы по ~2 мин, с метками времени для навигации
    paras, cur, cur_start = [], [], None
    for s in segs:
        if cur_start is None:
            cur_start = s["start"]
        cur.append(s["text"])
        if s["end"] - cur_start >= 120:
            paras.append(f"[{ts(cur_start, '.')[:8]}] " + " ".join(cur))
            cur, cur_start = [], None
    if cur:
        paras.append(f"[{ts(cur_start, '.')[:8]}] " + " ".join(cur))
    (out / f"{name}.txt").write_text("\n\n".join(paras) + "\n", encoding="utf-8")
    print(f"ГОТОВО: {len(segs)} сегментов, {(time.time() - t0) / 60:.1f} мин -> {out / (name + '.txt')}")


if __name__ == "__main__":
    main()
