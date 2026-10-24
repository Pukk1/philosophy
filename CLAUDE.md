# Философия — курс лекций от ментора

Ивану (аспирант ИТМО, инженер) ментор дал 7 видеолекций по философии и истории науки; позже пришлёт вопросы для самостоятельного разбора. Здесь: видео, расшифровки (Whisper), индекс для быстрого поиска, скрипты, документация.

Отвечать по-русски, сжато и плотно.

## Вопросы по содержанию лекций
Сначала прочитай [transcripts/index/how-to-search.md](transcripts/index/how-to-search.md). Расшифровки целиком не перечитывай.
- [transcripts/index/index.md](transcripts/index/index.md) — карта курса: темы, краткое содержание, разделы с таймкодами
- [transcripts/index/указатель.md](transcripts/index/указатель.md) — имена (~270) и термины (~170) → `Л<N> [чч:мм:сс]`
- [transcripts/index/оглавление/](transcripts/index/оглавление/) — подробное оглавление каждой лекции (термины с определениями лектора, персоналии, тезисы)
- `transcripts/index/лекция N (с таймкодами).txt` — расшифровки, абзацы ~2 мин с меткой `[чч:мм:сс]`; читать только нужный абзац
- В ответах ссылаться: «Л5, 00:13:42»; отделять позицию лектора от общих знаний

## Структура
```
лекция 1..7.mp4            видео (в .gitignore)
transcripts/               сырой вывод Whisper: лекция N.txt (сплошной), лекция N.srt (таймкоды)
transcripts/index/         индекс и расшифровки с таймкодами (источник правды для поиска)
scripts/                   расшифровка (run_gpu.*, lectureN.bat) и сборка индекса (srt2txt, build_index, normalize_index)
scripts/old/               прежние попытки: faster-whisper (transcribe.py), sherpa — не используются
docs/transcription-runbook.md   как запускать Whisper на GPU, что не работает
docs/agent-test.md         тест для нового агента: умеет ли пользоваться индексом
docs/claude-project.md     описание проекта claude.ai и соответствие документов файлам
docs/memory/               снимок памяти Claude по проекту (справочно)
work/, models/, .idea/     временные файлы, логи, модели, настройки IDE (в .gitignore)
```

## Пересборка индекса
1. `python scripts/srt2txt.py "transcripts/лекция N.srt" "transcripts/index/лекция N (с таймкодами).txt"` — для каждой лекции
2. Оглавления `transcripts/index/оглавление/лекция N.md` пишет Claude по расшифровке (формат — см. любой существующий файл; таймкоды только реальные из расшифровки)
3. `python scripts/build_index.py` → `index.md` + `указатель.raw.md`
4. `python scripts/normalize_index.py transcripts/index/указатель.raw.md transcripts/index/указатель.md` (маппинг имён ручной — проверять)

## Синхронизация с проектом claude.ai «Философия»
Те же файлы загружены в документы проекта (для поиска агентами в чатах): `transcripts/index.md`, `transcripts/указатель.md`, `transcripts/оглавление/лекция N.md`, `transcripts/лекция N.txt` (= здесь `лекция N (с таймкодами).txt`), `claude/how-to-search.md`, `claude/transcription-runbook.md`, `claude/agent-test.md` (= `docs/agent-test.md`). Полная таблица — `docs/claude-project.md`. Источник правды — эта папка; после правок перезалить в проект.
