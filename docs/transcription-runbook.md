# Транскрипция лекций — runbook

Как повторить или продолжить расшифровку лекций.

## Где что лежит (компьютер Ивана, Windows)
- Папка проекта: `C:\Users\Ivan\IdeaProjects\philosophy`
- Видео: `лекция 1.mp4` … `лекция 7.mp4` (0.9–1.4 ГБ каждая)
- Результаты Whisper: `transcripts\<имя>.txt` (сплошной текст) и `.srt` (с таймкодами)
- Скрипты: `scripts\`; старые варианты (faster-whisper, sherpa) — в `scripts\old\`
- GPU: RTX 3070 8 ГБ, драйвер 581.80 (CUDA 13.0)

## Запуск на GPU в Windows (рабочий способ)
- `scripts\lecture1.bat` … `scripts\lecture7.bat` — одна лекция; `scripts\all_lectures.bat` — все подряд, готовые пропускаются.
- Всё идёт через `scripts\run_gpu.bat N [модель]` → `scripts\run_gpu.py` на `C:\venvs\whisper38\Scripts\python.exe` (Python 3.8, openai-whisper 20250625, torch 2.4.1+cu121).
- Модель по умолчанию `large-v3-turbo`, лежит в `C:\Users\Ivan\.cache\whisper`.
- ffmpeg: `run_gpu.py` копирует бинарник из `imageio_ffmpeg` в `work\bin\ffmpeg.exe` и добавляет его в PATH.
- Лог: `work\gpu_run_<N>.log` (в начале `torch ... cuda: True` и имя GPU, в конце `[+] готово` и `[exit] 0`). Пишет `.part` и переименовывает по завершении.
- Скорость: лекция ~80 мин за ~3 мин.
- Bat-файлы держать только в ASCII и без `chcp 65001`, иначе cmd падает при запуске.
- Запускает Иван сам, двойным кликом. Claude читает логи и результаты через доступ к папке. Экраном не управлять без явного разрешения.

## Что не работает
- В PATH Windows нет Python (только заглушка Store), `py` нет. Системный Python 3.8 — `AppData\Local\Programs\Python\Python38`.
- faster-whisper (`scripts\old\transcribe.py`) требует Python ≥3.9.
- Linux-VM Claude не видит GPU; Hugging Face оттуда и из облака недоступен.

## Статус
- 2026-10-12: расшифрованы все 7 лекций; построен индекс (`transcripts\index\`, см. CLAUDE.md).
- Ожидается: список вопросов от ментора.
