$ErrorActionPreference = 'Continue'
$w = 'C:\Users\junio\Downloads\mango-vision\ALBUS26_major_revision\.worktrees\execution'
$c = 'C:\Users\junio\Downloads\mango-vision\ALBUS26_major_revision\.repro\final'
$log = 'C:\Users\junio\AppData\Local\Temp\claude\C--Users-junio-Downloads-mango-vision\8cb8439b-6f60-48c6-8aa8-a8206ee4af1a\scratchpad\repro.log'
"start $(Get-Date -Format s)" | Set-Content $log
if (Test-Path $c) { throw "$c exists" }
git -c core.longpaths=true -c core.autocrlf=false clone --quiet --no-hardlinks --config core.autocrlf=false $w $c 2>&1 | Add-Content $log
git -C $c config core.longpaths true
$head = git -C $w rev-parse HEAD; $clone = git -C $c rev-parse HEAD
"worktree HEAD $head clone HEAD $clone" | Add-Content $log
cmd /c mklink /J "$c\.venv" "$w\.venv" | Add-Content $log
Push-Location $c
$targets = @('experiments/model1/EXP-R02/metrics.json', 'experiments/model1/EXP-R02/predictions.jsonl',
             'experiments/model1/EXP-R02/predictions.jsonl.sha256', 'experiments/model1/EXP-R02/prediction_provenance.json',
             'artifacts/metrics/model1_intervals.json', 'artifacts/metrics/model2_intervals.json')
$before = @{}
foreach ($t in $targets) { $before[$t] = (Get-FileHash $t -Algorithm SHA256).Hash.ToLower(); Remove-Item $t }
"removed $($targets.Count) outputs $(Get-Date -Format s)" | Add-Content $log
& .\.venv\Scripts\python.exe -m src.evaluation.evaluate --model-id model1 --config configs/evaluation_frozen.json --split test --run-dir experiments/model1/EXP-R02 2>&1 | Add-Content $log
"evaluate exit $LASTEXITCODE $(Get-Date -Format s)" | Add-Content $log
& .\.venv\Scripts\python.exe -m src.statistics.intervals --predictions experiments/model1/EXP-R02/predictions.jsonl --groups data/manifests/model1_clean_manifest.csv --seed 42 --resamples 2000 --out artifacts/metrics/model1_intervals.json 2>&1 | Add-Content $log
"m1 intervals exit $LASTEXITCODE $(Get-Date -Format s)" | Add-Content $log
& .\.venv\Scripts\python.exe -m src.statistics.intervals --predictions experiments/model2/EXP-R03/predictions.jsonl --groups data/manifests/model2_frozen_manifest.csv --seed 42 --resamples 2000 --out artifacts/metrics/model2_intervals.json 2>&1 | Add-Content $log
"m2 intervals exit $LASTEXITCODE $(Get-Date -Format s)" | Add-Content $log
foreach ($t in $targets) {
    $after = if (Test-Path $t) { (Get-FileHash $t -Algorithm SHA256).Hash.ToLower() } else { 'MISSING' }
    "RESULT $t before=$($before[$t]) after=$after same=$($before[$t] -eq $after)" | Add-Content $log
}
git status --short 2>&1 | Add-Content $log
Pop-Location
"DONE $(Get-Date -Format s)" | Add-Content $log
