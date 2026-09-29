"""Read-only artifact inspection. Never imports ML frameworks or unpickles objects."""
from pathlib import Path
import csv
import hashlib
import json
import pickletools
import re
import zipfile

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent

def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1048576), b''):
            digest.update(block)
    return digest.hexdigest()

def static_metadata(ops, key):
    """Decode only primitive metadata grammar, rejecting every object opcode."""
    scalar = {'BINUNICODE', 'SHORT_BINUNICODE', 'UNICODE', 'BININT', 'BININT1', 'BININT2', 'INT', 'LONG1', 'BINFLOAT', 'NONE', 'NEWTRUE', 'NEWFALSE'}
    memo = {}
    for i, (op, arg, _) in enumerate(ops[:-1]):
        nxt, idx, _ = ops[i+1]
        if op.name in scalar and nxt.name in {'BINPUT', 'LONG_BINPUT'}:
            memo[idx] = True if op.name == 'NEWTRUE' else False if op.name == 'NEWFALSE' else arg
    start = next(i for i, (_, arg, _) in enumerate(ops) if arg == key) + 1
    while ops[start][0].name in {'BINPUT', 'LONG_BINPUT'}:
        start += 1
    stack = []
    mark = object()
    for op, arg, _ in ops[start:]:
        name = op.name
        if name in scalar:
            stack.append(True if name == 'NEWTRUE' else False if name == 'NEWFALSE' else arg)
        elif name in {'BINPUT', 'LONG_BINPUT'}:
            memo[arg] = stack[-1]
        elif name in {'BINGET', 'LONG_BINGET'}:
            stack.append(memo[arg])
        elif name == 'EMPTY_DICT': stack.append({})
        elif name == 'EMPTY_LIST': stack.append([])
        elif name == 'MARK': stack.append(mark)
        elif name in {'SETITEMS', 'APPENDS'}:
            at = max(i for i, x in enumerate(stack) if x is mark)
            values = stack[at+1:]
            del stack[at:]
            if name == 'SETITEMS': stack[-1].update(zip(values[::2], values[1::2]))
            else: stack[-1].extend(values)
            if len(stack) == 1: return stack[0]
        elif name == 'APPEND': stack[-2].append(stack.pop())
        elif name == 'SETITEM':
            val = stack.pop(); field = stack.pop(); stack[-1][field] = val
        else: raise ValueError(f'Rejected non-primitive opcode {name}')
    raise ValueError('Incomplete primitive metadata')

def main():
    checkpoints = [ROOT / p for p in (
        'Mango-vision/yolo11n-cls.pt',
        'Mango-vision/models/clasificador_enfermedad.pt',
        'SemilleroTI-Mangos/models/clasificador_enfermedad.pt',
        'SemilleroTI-Mangos/models/best.pt',
    )]
    metadata = []
    for path in checkpoints:
        info = {'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path), 'bytes': path.stat().st_size,
                'method': 'zipfile + pickletools.genops; no pickle.load, no torch.load, no inference'}
        with zipfile.ZipFile(path) as archive:
            info['members'] = [{'name': f.filename, 'size': f.file_size} for f in archive.infolist()]
            pkl = next(n for n in archive.namelist() if n.endswith('data.pkl'))
            ops = list(pickletools.genops(archive.read(pkl)))
            start = next((i for i, (_, arg, _) in enumerate(ops) if arg == 'train_args'), None)
            # Static opcode transcription only: REDUCE/GLOBAL are text, never executed.
            lines = [f'{pos}: {op.name} {arg!r}' for op, arg, pos in ops]
            dest = OUT / (path.parent.name + '_' + path.stem + '_pickle_opcodes.txt')
            if path.parent.name == 'models':
                dest = OUT / (path.parent.parent.name + '_' + path.stem + '_pickle_opcodes.txt')
            dest.write_text('\n'.join(lines), encoding='utf-8')
            info['opcode_transcription'] = dest.relative_to(ROOT).as_posix()
            info['selected_string_context'] = {}
            keys = {'date', 'version', 'train_args', 'train_metrics', 'train_results', 'epoch', 'best_fitness'}
            for i, (op, arg, pos) in enumerate(ops):
                if isinstance(arg, str) and arg in keys:
                    info['selected_string_context'].setdefault(arg, []).append(lines[i:i+14])
            info['tail_after_train_args'] = lines[start:] if start is not None else []
            info['decoded_primitive_metadata'] = {}
            for key in ['train_args', 'train_metrics', 'train_results']:
                try:
                    value = static_metadata(ops, key)
                    info['decoded_primitive_metadata'][key] = value
                    if key == 'train_results' and value:
                        history = OUT / (path.parent.parent.name + '_' + path.stem + '_embedded_train_results.csv')
                        with history.open('w', encoding='utf-8', newline='') as f:
                            writer = csv.writer(f); writer.writerow(value.keys()); writer.writerows(zip(*value.values()))
                except (ValueError, KeyError, StopIteration) as exc:
                    info['decoded_primitive_metadata'][key] = {'unverified': str(exc)}
        metadata.append(info)
    (OUT / 'checkpoint_static_metadata.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding='utf-8')
    csv_path = ROOT / 'SemilleroTI-Mangos/docs/Yolo26n-model-docs/Entrenamiento-1/resultados/results.csv'
    with csv_path.open(encoding='utf-8-sig') as f:
        rows = [{k.strip(): float(v) for k, v in row.items()} for row in csv.DictReader(f)]
    metrics = ['metrics/mAP50(B)', 'metrics/mAP50-95(B)', 'metrics/precision(B)', 'metrics/recall(B)']
    arithmetic = {'method': 'CSV transcription and arithmetic, NOT experimental metric reproduction', 'rows': len(rows),
                  'last': rows[-1], 'maxima': {key: max(rows, key=lambda r:r[key]) for key in metrics},
                  'max_recall_excluding_epoch1': max(rows[1:], key=lambda r:r['metrics/recall(B)'])}
    for file in ['confusion_matrix_cls.csv', 'confusion_matrix_raw.csv']:
        with (ROOT / 'Articulo/reports' / file).open(encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            labels = next(reader)
            matrix = [[int(v) for v in row] for row in reader]
        total = sum(map(sum, matrix))
        diagonal = sum(matrix[i][i] for i in range(len(matrix)))
        classes = len(matrix) if file == 'confusion_matrix_cls.csv' else len(matrix)-1
        per_class = []
        for i in range(classes):
            tp = matrix[i][i]
            support = sum(matrix[i])
            pred = sum(row[i] for row in matrix)
            precision = tp / pred if pred else 0
            recall = tp / support if support else 0
            f1 = 2*precision*recall/(precision+recall) if precision+recall else 0
            per_class.append({'class':labels[i], 'tp':tp, 'support':support, 'predicted':pred, 'precision':precision, 'recall':recall, 'f1':f1})
        arithmetic[file] = {'labels':labels, 'matrix':matrix, 'sum_cells':total, 'diagonal':diagonal,
                            'diagonal_over_sum_cells':diagonal/total, 'per_class':per_class,
                            'macro_f1':sum(c['f1'] for c in per_class)/classes}
    (OUT / 'csv_arithmetic_check.json').write_text(json.dumps(arithmetic, ensure_ascii=False, indent=2), encoding='utf-8')
    assert arithmetic['rows'] == 150
    assert arithmetic['confusion_matrix_cls.csv']['sum_cells'] == 219
    assert arithmetic['confusion_matrix_cls.csv']['diagonal'] == 199
    assert metadata[1]['sha256'] == metadata[2]['sha256']
    print(json.dumps({'checkpoint_hashes':{x['path']:x['sha256'] for x in metadata},
                      'rows': len(rows), 'maxima':{k:{'epoch':v['epoch'],'value':v[k]} for k,v in arithmetic['maxima'].items()},
                      'checks':'PASS (static evidence only)'}, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
