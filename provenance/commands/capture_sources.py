from pathlib import Path
import csv, hashlib, os, json, subprocess, datetime
ROOT=Path(r'C:\Users\junio\Downloads\mango-vision')
OUT=ROOT/'ALBUS26_major_revision'
def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()
assert hashlib.sha256(b'abc').hexdigest()=='ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'
rows=[]
for parent,dirs,files in os.walk(ROOT):
    dirs[:]=sorted(d for d in dirs if d not in {'.git','.venv','ALBUS26_major_revision','node_modules','__pycache__'})
    for name in sorted(files):
        p=Path(parent)/name
        s=p.stat()
        rows.append(dict(source_id='SRC-'+str(len(rows)+1).zfill(6),path=str(p),relative_path=p.relative_to(ROOT).as_posix(),size_bytes=s.st_size,mtime_ns=s.st_mtime_ns,modified_utc=datetime.datetime.fromtimestamp(s.st_mtime,datetime.timezone.utc).isoformat(),type=p.suffix.lower(),sha256=digest(p)))
mail=Path(r'C:\Users\junio\Downloads\Correo_ JORGE JUNIOR SOLANO ROMERO - Outlook.pdf')
s=mail.stat()
rows.append(dict(source_id='SRC-MAIL',path=str(mail),relative_path='../'+mail.name,size_bytes=s.st_size,mtime_ns=s.st_mtime_ns,modified_utc=datetime.datetime.fromtimestamp(s.st_mtime,datetime.timezone.utc).isoformat(),type='.pdf',sha256=digest(mail)))
with (OUT/'provenance/source_manifest.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
from collections import Counter
summary={'files':len(rows),'bytes':sum(r['size_bytes'] for r in rows),'types':dict(Counter(r['type'] for r in rows)),'exclusions':['.git','.venv','node_modules','__pycache__','ALBUS26_major_revision'],'capture_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
(OUT/'provenance/environment/inventory_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
commands=['rev-parse --show-toplevel','status --short','branch --show-current','rev-parse HEAD','log --oneline -n 20','worktree list --porcelain','rev-parse --git-dir --git-common-dir --show-superproject-working-tree']
parts=['# Estado inicial del repositorio\n\n'+summary['capture_utc']+'\n\nCaptura antes de investigación profunda. Exclusiones del hash: .git, .venv, node_modules, __pycache__. Se conserva status Git para distinguir cambios previos; exclusiones no se certifican byte a byte.\n']
for loc in [ROOT,ROOT/'Mango-vision',ROOT/'SemilleroTI-Mangos']:
    parts.append('\n## '+str(loc)+'\n')
    for command in commands:
        r=subprocess.run(['git','-C',str(loc)]+command.split(),capture_output=True,text=True,encoding='utf-8',errors='replace',env={**os.environ,'GIT_OPTIONAL_LOCKS':'0'})
        parts.append(f'\n### git {command}\nExit code: {r.returncode}\n```text\n{r.stdout}{r.stderr}```\n')
(OUT/'provenance/repository_initial_state.md').write_text(''.join(parts),encoding='utf-8')
print(json.dumps(summary))
from pypdf import PdfReader
for path,name in [(ROOT/'Articulo_Mango_ALBUS.pdf','submitted_candidate'),(mail,'review_email')]:
    reader=PdfReader(path)
    (OUT/f'reports/{name}_text.txt').write_text('\n\n'.join(f'=== PAGE {i+1} ===\n'+(p.extract_text() or '') for i,p in enumerate(reader.pages)),encoding='utf-8')
    print(name,len(reader.pages),reader.metadata)
