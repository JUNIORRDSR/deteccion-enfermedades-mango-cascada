"""Read-only source verification and documentary checks, never model execution."""
from pathlib import Path
from collections import Counter, defaultdict
import csv, datetime, hashlib, json, os, re, subprocess, sys, unicodedata, zipfile
import xml.etree.ElementTree as ET

W=Path(__file__).resolve().parents[2]
R=W.parent
OUT=W/'reports/first_phase_verification.json'
def digest(path):
    with path.open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()
def rows(path):
    with path.open(encoding='utf-8-sig',newline='') as f: return list(csv.DictReader(f))
def unique(items,key):
    ids=[r[key] for r in items]
    assert all(ids) and len(ids)==len(set(ids)), key
assert hashlib.sha256(b'abc').hexdigest()=='ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'
report={'checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'command':[sys.executable,str(Path(__file__).resolve())],
        'scope':'First-phase documentary verification; no model inference, training, new split or pHash',
        'checks':{},'errors':[]}

def run():
    source=rows(W/'provenance/source_manifest.csv');unique(source,'source_id')
    baseline_hash=digest(W/'provenance/source_manifest.csv')
    changes=[];missing=[];timestamp_changes=[]
    for row in source:
        path=Path(row['path'])
        if not path.is_file(): missing.append(row['source_id']);continue
        stat=path.stat()
        if stat.st_size!=int(row['size_bytes']) or digest(path)!=row['sha256']: changes.append(row['source_id'])
        if stat.st_mtime_ns!=int(row['mtime_ns']): timestamp_changes.append(row['source_id'])
    excluded={'.git','.venv','ALBUS26_major_revision','node_modules','__pycache__'}
    observed=set()
    for parent,dirs,files in os.walk(R):
        dirs[:]=[d for d in dirs if d not in excluded]
        observed.update(str((Path(parent)/name).resolve()) for name in files)
    expected={str(Path(r['path']).resolve()) for r in source if r['source_id']!='SRC-MAIL'}
    report['checks']['legacy']={'files':len(source),'bytes':sum(int(r['size_bytes']) for r in source),
        'changed':changes,'missing':missing,'new_eligible_paths':sorted(observed-expected),
        'missing_eligible_paths':sorted(expected-observed),'mtime_changes':timestamp_changes,
        'baseline_sha256':baseline_hash,'exclusions':sorted(excluded)}
    assert not changes and not missing and observed==expected, 'legacy source differences'
    assert digest(W/'provenance/source_manifest.csv')==baseline_hash, 'baseline overwritten'
    initial=(W/'provenance/repository_initial_state.md').read_text(encoding='utf-8')
    git_checks=[]
    for name in ['Mango-vision','SemilleroTI-Mangos']:
        section=initial.split('## '+str(R/name)+'\n')[1].split('\n## ')[0]
        for command in ['status --short','branch --show-current','rev-parse HEAD','worktree list --porcelain']:
            body=section.split('### git '+command+'\n')[1].split('\n### ')[0]
            old=re.search(r'```text\n([\s\S]*?)```',body).group(1)
            proc=subprocess.run(['git','-C',str(R/name),*command.split()],capture_output=True,text=True,
                encoding='utf-8',errors='replace',env={**os.environ,'GIT_OPTIONAL_LOCKS':'0'})
            item=dict(repo=name,command='git '+command,exit_code=proc.returncode,stdout=proc.stdout,stderr=proc.stderr,
                      matches_initial=(proc.returncode==0 and proc.stdout==old))
            git_checks.append(item)
    report['checks']['git']=git_checks
    assert all(x['matches_initial'] for x in git_checks), 'git state changed'

    claims=rows(W/'docs/research/claim_evidence_matrix.csv')
    reviews=rows(W/'reports/reviewer_matrix.csv')
    experiments=rows(W/'provenance/experiment_registry.csv')
    artifacts=rows(W/'provenance/artifact_registry.csv')
    derived=rows(W/'provenance/derived_evidence_registry.csv')
    for table,key in [(claims,'claim_id'),(reviews,'review_id'),(experiments,'experiment_id'),(artifacts,'artifact_id'),(derived,'evidence_id')]: unique(table,key)
    assert (len(claims),len(reviews),len(experiments),len(artifacts))==(50,18,9,100)
    assert all(r['reproduced']=='NO' for r in experiments+artifacts)
    src_index={r['source_id']:r for r in source}
    exp_ids={r['experiment_id'] for r in experiments}
    evidence_ids=set(src_index)|{r['evidence_id'] for r in derived}|{r['artifact_id'] for r in artifacts}
    for row in claims:
        assert set(re.findall(r'(?:SRC-\d+|SRC-MAIL|DER-\d+|ART-\d+)',row['evidence_id']))<=evidence_ids, row['claim_id']
        assert set(re.findall(r'EXP-\d+',row['experiment_id']))<=exp_ids, row['claim_id']
    for row in artifacts:
        if row['source_id']=='DERIVED_THIS_AUDIT':
            path=(R/row['path']).resolve()
            assert path.is_relative_to(W) and path.is_file(), row['artifact_id']
            assert row['sha256']==digest(path), row['artifact_id']
        else:
            assert row['source_id'] in src_index, row['artifact_id']
            assert row['sha256']==src_index[row['source_id']]['sha256'], row['artifact_id']
    for row in derived: assert digest(W/row['path'])==row['sha256'], row['evidence_id']

    required=['README.md','docs/research/research_charter.md','docs/research/source_inventory.md',
        'docs/research/manuscript_genealogy.md','docs/research/reviewer_matrix.md','docs/research/claim_evidence_matrix.csv',
        'docs/research/decision_log.md','docs/research/risk_register.md','docs/research/methodology_decisions.md',
        'docs/research/experiment_log.md','docs/research/changelog_revision.md','docs/response_to_reviewers.md',
        'reports/spec_self_review.md','reports/plan_self_review.md','reports/first_phase_executive_report.md',
        'reports/research_independent_review.md','reports/design_review_resolution.md',
        'docs/superpowers/specs/2026-09-17-albus26-major-revision-design.md',
        'docs/superpowers/plans/2026-09-17-albus26-major-revision.md']
    for relative in required: assert (W/relative).is_file() and (W/relative).stat().st_size, relative
    plan=(W/required[-1]).read_text(encoding='utf-8')
    task_ids=set(re.findall(r'^## (TASK-\d+)',plan,re.M))
    assert task_ids=={f'TASK-{i:02}' for i in range(1,11)}
    for part in re.split(r'^## TASK-\d+[^\n]*',plan,flags=re.M)[1:]:
        for field in ['FILES','CONSUMES','PRODUCES','PRECONDITIONS','STEPS','TESTS / VERIFICATION COMMANDS','EXPECTED RESULTS','ARTIFACTS','REVIEW-IDs SATISFIED']:
            assert f'**{field}:**' in part, field
    for row in reviews:
        assert set(row['implementation_tasks'].split(';'))<=task_ids, row['review_id']
        assert row['status'] in {'PENDING_APPROVAL','BLOCKED'}, row['review_id']
    spec=(W/required[-2]).read_text(encoding='utf-8')
    assert not re.search(r'\b(?:TODO|TBD)\b|definir después|según corresponda',spec+'\n'+plan,re.I)
    assert '- [x]' not in plan
    executive=(W/'reports/first_phase_executive_report.md').read_text(encoding='utf-8')
    assert len(re.findall(r'^## \d+\.',executive,re.M))==17
    for path in re.findall(r'\]\(<(C:/[^>]+)>\)',executive):
        if path.endswith('/docs/final_validation_report.md'): continue  # generated from this result
        assert Path(path).exists(), 'Broken executive link: '+path
    report['checks']['documentary']={'claims':len(claims),'reviews':len(reviews),'experiments':len(experiments),'artifacts':len(artifacts),
                                   'derived_evidence':len(derived),'tasks':len(task_ids),'executive_answers':17,
                                   'required_documents':len(required),'all_experiments_reproduced_NO':True,
                                   'hashes':{p:digest(W/p) for p in required}}
    for directory in ['src','tests','experiments','manuscript/source','manuscript/output']:
        assert not any(p.is_file() for p in (W/directory).rglob('*')), 'Unexpected implementation: '+directory

    inv=rows(W/'data/manifests/legacy_dataset_inventory.csv')
    assert len(inv)==7016
    for row in inv:
        assert src_index[row['source_id']]['sha256']==row['sha256'],row['source_id']
        if row['label_source_id']: assert src_index[row['label_source_id']]['sha256']==row['label_sha256']
    counts=Counter((r['dataset_id'],r['split']) for r in inv)
    m1=[r for r in inv if r['dataset_id']=='DATA-001']
    assert len(m1)==669 and sum(int(r['annotation_count']) for r in m1)==1854
    m1test=[r for r in m1 if r['split']=='test']
    assert len(m1test)==33 and sum(int(r['annotation_count']) for r in m1test)==99
    label_counts=Counter()
    for row in m1test:
        for line in (R/row['label_path']).read_text(encoding='utf-8').splitlines():
            if line.strip(): label_counts[int(line.split()[0])]+=1
    assert label_counts==Counter({0:13,1:86})
    duplicates={}
    for dataid in ['DATA-001','DATA-003','DATA-004','DATA-005']:
        groups=defaultdict(list)
        for row in inv:
            if row['dataset_id']==dataid:groups[row['sha256']].append(row['split'])
        n=sum(a!=b for group in groups.values() for i,a in enumerate(group) for b in group[i+1:])
        duplicates[dataid]=n
    assert duplicates=={'DATA-001':0,'DATA-003':41,'DATA-004':0,'DATA-005':0}
    report['checks']['inventory']={'images':len(inv),'counts':{f'{k[0]}/{k[1]}':v for k,v in sorted(counts.items())},
         'm1_test_instances':dict(label_counts),'exact_cross_split_pairs':duplicates,'scope':'Binary identity only; no new perceptual audit'}

    with (R/'Articulo/reports/confusion_matrix_cls.csv').open(encoding='utf-8-sig',newline='') as f:
        raw=list(csv.reader(f))
    cm=[[int(x) for x in row] for row in raw[1:]]
    assert len(cm)==5 and all(len(row)==5 for row in cm), 'Expected 5x5 matrix without row-label column'
    total=sum(map(sum,cm));correct=sum(cm[i][i] for i in range(5))
    f1=[2*cm[i][i]/(sum(cm[i])+sum(row[i] for row in cm)) for i in range(5)]
    macro=sum(f1)/5
    assert (total,correct)==(219,199) and f'{macro:.3f}'=='0.909' and f'{f1[1]:.3f}'=='0.831'
    report['checks']['existing_csv_arithmetic']={'total':total,'correct':correct,'accuracy':correct/total,'macro_f1':macro,'cancro_f1':f1[1],
                                              'experimental_reproduction':False}

    from pypdf import PdfReader
    pdf=PdfReader(R/'Articulo_Mango_ALBUS.pdf')
    pdftext='\n'.join(p.extract_text() or '' for p in pdf.pages)
    pdftext=re.sub(r'Author \| short title \d+','',pdftext)
    pdftext=re.sub(r'ALBUS 2025, 3, x\. https://doi.org/ www.albus.lat','',pdftext)
    with zipfile.ZipFile(R/'Articulo_Mango_ALBUS.docx') as z:
        docxtext=' '.join(ET.fromstring(z.read('word/document.xml')).itertext())
        # Only w:t content is manuscript text; element attributes and drawing metadata are excluded.
        ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        docxtext=' '.join(x.text or '' for x in ET.fromstring(z.read('word/document.xml')).findall('.//w:t',ns))
    def norm(text):return ''.join(c for c in unicodedata.normalize('NFKD',text.lower()) if c.isalnum())
    a,b=norm(pdftext),norm(docxtext)
    assert a==b and len(a)==33468, 'PDF/DOCX normalization differs'
    report['checks']['genealogy']={'pages':len(pdf.pages),'normalized_equal':a==b,'characters':len(a),
                                 'sha256':hashlib.sha256(a.encode()).hexdigest(),'fresh_extraction':True,'layout_equivalence':False}
    report['status']='PASS_FIRST_PHASE_DOCUMENTARY'

try:
    run()
except Exception as exc:
    report['status']='FAIL';report['errors'].append(f'{type(exc).__name__}: {exc}')
OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'status':report['status'],'errors':report['errors'],'checks':list(report['checks']),
                  'report':str(OUT),'checked_at_utc':report['checked_at_utc']},ensure_ascii=False))
sys.exit(0 if report['status']=='PASS_FIRST_PHASE_DOCUMENTARY' else 1)
