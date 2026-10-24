"""Расшифровка лекции на GPU под Windows через openai-whisper из C:\\venvs\\whisper38.

Запуск (через scripts\\run_gpu.bat):  python scripts\\run_gpu.py 2 [модель]
Скрипт лежит в scripts\\, лекции и transcripts\\ — в родительской папке.
Модель по умолчанию large-v3-turbo (уже лежит в %USERPROFILE%\\.cache\\whisper).
Результат: transcripts\\<имя>.txt и .srt; прерванный запуск оставляет только .part.
"""
import os
import shutil
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent  # корень проекта (папка с лекциями)
os.chdir(HERE)

# openai-whisper вызывает "ffmpeg" из PATH; берём бинарник из imageio_ffmpeg
import imageio_ffmpeg  # noqa: E402

bin_dir = HERE / "work" / "bin"
bin_dir.mkdir(parents=True, exist_ok=True)
ff = bin_dir / "ffmpeg.exe"
if not ff.exists():
    shutil.copy(imageio_ffmpeg.get_ffmpeg_exe(), ff)
os.environ["PATH"] = str(bin_dir) + os.pathsep + os.environ["PATH"]

import torch  # noqa: E402
import whisper  # noqa: E402

print("torch", torch.__version__, "cuda:", torch.cuda.is_available(), flush=True)
if not torch.cuda.is_available():
    sys.exit("[FAIL] CUDA недоступна для torch")
print("GPU:", torch.cuda.get_device_name(0), flush=True)

num = sys.argv[1] if len(sys.argv) > 1 else "2"
model_name = sys.argv[2] if len(sys.argv) > 2 else "large-v3-turbo"
matches = sorted(HERE.glob("* %s.mp4" % num))
if not matches:
    sys.exit("[FAIL] не найден файл лекции %s" % num)
src = matches[0]

out_dir = HERE / "transcripts"
out_dir.mkdir(exist_ok=True)
txt_path = out_dir / (src.stem + ".txt")
srt_path = out_dir / (src.stem + ".srt")
if txt_path.exists():
    print("[=] уже есть, пропуск: %s" % txt_path.name)
    sys.exit(0)


def ts(sec):
    ms = int(round(sec * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return "%02d:%02d:%02d,%03d" % (h, m, s, ms)


print("[model]", model_name, flush=True)
model = whisper.load_model(model_name, device="cuda")
print("[>]", src.name, flush=True)
t0 = time.time()
result = model.transcribe(
    str(src),
    language="ru",
    fp16=True,
    condition_on_previous_text=False,
    verbose=False,
)

txt_tmp = Path(str(txt_path) + ".part")
srt_tmp = Path(str(srt_path) + ".part")
with open(txt_tmp, "w", encoding="utf-8") as ftxt, open(srt_tmp, "w", encoding="utf-8") as fsrt:
    for i, seg in enumerate(result["segments"], 1):
        text = seg["text"].strip()
        ftxt.write(text + "\n")
        fsrt.write("%d\n%s --> %s\n%s\n\n" % (i, ts(seg["start"]), ts(seg["end"]), text))
txt_tmp.replace(txt_path)
srt_tmp.replace(srt_path)
print("[+] готово за %.1f мин -> %s" % ((time.time() - t0) / 60, txt_path), flush=True)
