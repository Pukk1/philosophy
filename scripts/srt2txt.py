"""Пересборка абзацев из .srt: python scripts/srt2txt.py "transcripts/лекция N.srt" "transcripts/index/лекция N (с таймкодами).txt"
Склеивает реплики, пока не пройдёт >=110 c и реплика не закончится на .?!» ; каждый абзац начинается с [чч:мм:сс]."""
import re,sys,pathlib
src,dst=sys.argv[1],sys.argv[2]
n=pathlib.Path(src).stem
blocks=re.split(r'\n\s*\n',pathlib.Path(src).read_text(encoding='utf-8-sig').strip())
cues=[]
for b in blocks:
    l=b.strip().splitlines()
    if len(l)<3: continue
    t=l[1].split(' --> ')[0].split(',')[0]
    cues.append((t,' '.join(x.strip() for x in l[2:])))
def sec(t):h,m,s=map(int,t.split(':'));return h*3600+m*60+s
out=[f'# {n.capitalize()}\n',f'Расшифровка (Whisper). Абзацы ≈ по 2 минуты, метка [чч:мм:сс] — начало абзаца.\n']
cur=[];start=None
for t,x in cues:
    if start is None: start=t
    cur.append(x)
    if sec(t)-sec(start)>=110 and x.rstrip().endswith(('.','?','!','»')):
        out.append(f'[{start}] '+' '.join(cur)+'\n');cur=[];start=None
if cur: out.append(f'[{start}] '+' '.join(cur)+'\n')
pathlib.Path(dst).write_text('\n'.join(out),encoding='utf-8')
print(dst,len(out)-2)
