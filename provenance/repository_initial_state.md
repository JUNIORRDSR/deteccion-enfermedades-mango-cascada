# Estado inicial del repositorio

2026-09-17T17:17:58.770289+00:00

Captura antes de investigación profunda. Exclusiones del hash: .git, .venv, node_modules, __pycache__. Se conserva status Git para distinguir cambios previos; exclusiones no se certifican byte a byte.

## C:\Users\junio\Downloads\mango-vision

### git rev-parse --show-toplevel
Exit code: 128
```text
fatal: not a git repository (or any of the parent directories): .git
```

### git status --short
Exit code: 128
```text
fatal: not a git repository (or any of the parent directories): .git
```

### git branch --show-current
Exit code: 128
```text
fatal: not a git repository (or any of the parent directories): .git
```

### git rev-parse HEAD
Exit code: 128
```text
fatal: not a git repository (or any of the parent directories): .git
```

### git log --oneline -n 20
Exit code: 128
```text
fatal: not a git repository (or any of the parent directories): .git
```

### git worktree list --porcelain
Exit code: 128
```text
fatal: not a git repository (or any of the parent directories): .git
```

### git rev-parse --git-dir --git-common-dir --show-superproject-working-tree
Exit code: 128
```text
fatal: not a git repository (or any of the parent directories): .git
```

## C:\Users\junio\Downloads\mango-vision\Mango-vision

### git rev-parse --show-toplevel
Exit code: 0
```text
C:/Users/junio/Downloads/mango-vision/Mango-vision
```

### git status --short
Exit code: 0
```text
```

### git branch --show-current
Exit code: 0
```text
main
```

### git rev-parse HEAD
Exit code: 0
```text
e7e59d1bce74a7ae12674f5b6068068681e691ce
```

### git log --oneline -n 20
Exit code: 0
```text
e7e59d1 data(DatasetMango_Propias): agrega test externo anotado en Roboflow
136930b fix(data): deduplicar MangoDHDS y documentar pipeline end-to-end
d00e8a9 Merge branch 'main' of https://github.com/JUNIORRDSR/Mango-vision
555c262 Merge pull request #1 from JUNIORRDSR/claude/mango-antracnose-detection-KJ7se
e9ac0f4 feat: scaffolding de pipeline en cascada para deteccion de enfermedades en mango
d2bb398 feat: se agregaron dataset personal y original de mendeley
f63be3f data(DatasetMango_YOLO): se subio el dataset de prueba
d0529f6 Initial commit
```

### git worktree list --porcelain
Exit code: 0
```text
worktree C:/Users/junio/Downloads/mango-vision/Mango-vision
HEAD e7e59d1bce74a7ae12674f5b6068068681e691ce
branch refs/heads/main

```

### git rev-parse --git-dir --git-common-dir --show-superproject-working-tree
Exit code: 0
```text
.git
.git
```

## C:\Users\junio\Downloads\mango-vision\SemilleroTI-Mangos

### git rev-parse --show-toplevel
Exit code: 0
```text
C:/Users/junio/Downloads/mango-vision/SemilleroTI-Mangos
```

### git status --short
Exit code: 0
```text
 M api/__pycache__/main.cpython-313.pyc
 M api/routers/__pycache__/history.cpython-313.pyc
 M api/routers/__pycache__/inference.cpython-313.pyc
 M core/__pycache__/config.cpython-313.pyc
 M core/__pycache__/database.cpython-313.pyc
 M core/__pycache__/vision.cpython-313.pyc
 M mango_detecciones.db
?? core/__pycache__/cascade.cpython-313.pyc
?? core/cascade.py
?? data/
?? docs/MangosDataset/test/labels.cache
?? models/clasificador_enfermedad.pt
?? run_cascade.py
```

### git branch --show-current
Exit code: 0
```text
main
```

### git rev-parse HEAD
Exit code: 0
```text
98614804dd967e19a77af9fc58c27364d2e43bc9
```

### git log --oneline -n 20
Exit code: 0
```text
9861480 docs(Docs/-Readme):documentar las especificaciones técnicas del sistema.
e1477b5 app(all): primera version funcional
e5ad58d docs(readme): agregar readme con estructura y guia de instalacion del proyecto
```

### git worktree list --porcelain
Exit code: 0
```text
worktree C:/Users/junio/Downloads/mango-vision/SemilleroTI-Mangos
HEAD 98614804dd967e19a77af9fc58c27364d2e43bc9
branch refs/heads/main

```

### git rev-parse --git-dir --git-common-dir --show-superproject-working-tree
Exit code: 0
```text
.git
.git
```
