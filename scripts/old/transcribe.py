"""Транскрипция лекций (mp4/mp3/wav/...) через faster-whisper.

Примеры:
    python transcribe.py                      # все видео в текущей папке
    python transcribe.py "лекция 1.mp4"       # один файл
    python transcribe.py . --model medium     # модель полегче/побыстрее
"""
import argparse
import sys
import time
from pathlib import Path

from faster_whisper import WhisperModel

MEDIA_EXT = {".mp4", ".mkv", ".mov", ".avi", ".webm", ".mp3", ".m4a", ".wav", ".flac", ".ogg"}


def detect_device() -> tuple[str, str]:
    try:
        import ctranslate2
        if ctranslate2.get_cuda_device_count() > 0:
            return "cuda", "float16"
    except Exception:
        pass
    return "cpu", "int8"


def collect(inputs: list[str]) -> list[Path]:
    files: list[Path] = []
    for raw in inputs:
        p = Path(raw)
        if p.is_dir():
            files += sorted(f for f in p.iterdir() if f.suffix.lower() in MEDIA_EXT)
        elif p.is_file():
            files.append(p)
        else:
            print(f"[!] не найдено: {p}", file=sys.stderr)
    return files


def ts(sec: float) -> str:
    ms = int(round(sec * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def transcribe(model: WhisperModel, src: Path, out_dir: Path, lang: str, force: bool) -> None:
    txt_path = out_dir / f"{src.stem}.txt"
    srt_path = out_dir / f"{src.stem}.srt"
    if txt_path.exists() and not force:
        print(f"[=] пропуск (уже есть): {txt_path.name}")
        return

    print(f"[>] {src.name}")
    t0 = time.time()
    segments, info = model.transcribe(
        str(src),
        language=lang,
        beam_size=5,
        vad_filter=True,                      # выкидывает паузы, меньше галлюцинаций
        vad_parameters={"min_silence_duration_ms": 500},
        condition_on_previous_text=False,     # защита от зацикливания на длинных записях
    )
    total = info.duration

    # пишем во временные файлы, чтобы прерванный запуск не оставил «готовый» txt
    txt_tmp, srt_tmp = txt_path.with_suffix(".txt.part"), srt_path.with_suffix(".srt.part")
    with open(txt_tmp, "w", encoding="utf-8") as ftxt, open(srt_tmp, "w", encoding="utf-8") as fsrt:
        for i, seg in enumerate(segments, 1):
            text = seg.text.strip()
            ftxt.write(text + "\n")
            fsrt.write(f"{i}\n{ts(seg.start)} --> {ts(seg.end)}\n{text}\n\n")
            print(f"\r    {seg.end / total:6.1%}  [{ts(seg.end)[:8]} / {ts(total)[:8]}]", end="", flush=True)
    txt_tmp.replace(txt_path)
    srt_tmp.replace(srt_path)
    print(f"\n[+] готово за {(time.time() - t0) / 60:.1f} мин -> {txt_path}")


def main() -> None:
    ap = argparse.ArgumentParser(description="Транскрипция лекций через faster-whisper")
    ap.add_argument("inputs", nargs="*", default=["."], help="файлы или папки (по умолчанию текущая)")
    ap.add_argument("-m", "--model", default="large-v3",
                    help="tiny / base / small / medium / large-v3 / large-v3-turbo (по умолч. large-v3)")
    ap.add_argument("-l", "--language", default="ru")
    ap.add_argument("-o", "--out", default="transcripts", help="папка для результатов")
    ap.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    ap.add_argument("--force", action="store_true", help="перезаписать уже готовые")
    args = ap.parse_args()

    files = collect(args.inputs)
    if not files:
        sys.exit("Нет файлов для обработки")

    device, compute = detect_device() if args.device == "auto" else (
        args.device, "float16" if args.device == "cuda" else "int8")
    print(f"Модель {args.model}, устройство {device} ({compute}), файлов: {len(files)}")
    model = WhisperModel(args.model, device=device, compute_type=compute)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    for f in files:
        transcribe(model, f, out_dir, args.language, args.force)


if __name__ == "__main__":
    main()
