"""Собирает transcripts/index/index.md и черновой указатель.md из оглавлений.
Запуск из корня репозитория: python scripts/build_index.py
Черновой указатель потом нормализуется (слияние дублей имён) — scripts/normalize_index.py
(маппинг имён в нём ручной, написан под текущие оглавления)."""
import re,pathlib,collections
ROOT=pathlib.Path(__file__).resolve().parent.parent/'transcripts'/'index'
D=ROOT/'оглавление'
names=collections.defaultdict(list);terms=collections.defaultdict(list)
over=['# Курс: оглавление лекций\n',
'Навигация по 7 лекциям. Полные расшифровки — `лекция N (с таймкодами).txt` (абзацы с меткой [чч:мм:сс]). Подробные оглавления — `оглавление/лекция N.md`. Предметно-именной указатель — `указатель.md`.\n',
'Как искать: сначала здесь/в указателе → таймкод → нужный абзац в расшифровке (метки совпадают).\n']
for i in range(1,8):
    t=(D/f'лекция {i}.md').read_text(encoding='utf-8')
    parts=re.split(r'^### ',t,flags=re.M)
    head=parts[0].strip().splitlines()
    title=head[0].lstrip('# ').strip()
    rest={p.split('\n',1)[0].strip():p.split('\n',1)[1] for p in parts[1:]}
    over.append(f'\n## {title}\n'+'\n'.join(head[1:])+'\n\n**Разделы:**\n'+'\n'.join(l.split(' — ')[0] for l in rest.get('Разделы','').splitlines() if l.startswith('- ')))
    for k,store in (('Персоналии',names),('Понятия',terms)):
        body=next((v for kk,v in rest.items() if kk.startswith(k)),'')
        for l in body.splitlines():
            if not l.startswith('- '):continue
            seg=l[2:].split(' — ')
            ts=re.findall(r'\[\d\d:\d\d:\d\d\]',l)
            gist=seg[-1].strip() if len(seg)>2 else ''
            store[seg[0].strip()].append(f'Л{i} '+', '.join(ts[:4])+(f' — {gist}' if gist else ''))
def dump(title,store):
    return '\n'.join([f'\n## {title}\n']+[f'- **{k}** — '+'; '.join(store[k]) for k in sorted(store,key=lambda s:s.lower().lstrip('«"'))])
(ROOT/'index.md').write_text('\n'.join(over)+'\n',encoding='utf-8')
(ROOT/'указатель.raw.md').write_text('# Указатель (черновой)\n'+dump('Персоналии и тексты',names)+'\n'+dump('Понятия и термины',terms)+'\n',encoding='utf-8')
