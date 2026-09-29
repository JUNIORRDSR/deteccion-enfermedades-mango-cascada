"""Preserve reproducible CPU topology and benchmark-context probes.

Closes the residual of finding M-03: the earlier record cited a probe that reads
only ProcessorNameString, so the physical-core count had no preserved command or
raw output. TASK-06 needs the run-linked context too.
"""

import datetime
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from src.evaluation.provenance import authorized_root, check_output  # noqa: E402

REG = 'HKLM:' + chr(92) + 'HARDWARE' + chr(92) + 'DESCRIPTION' + chr(92) + 'System' + chr(92) + 'CentralProcessor'

REQUIRED = ('processor_name', 'topology_cim', 'topology_env', 'logical_registry_count', 'os_build')

PROBES = {
    'processor_name': "(Get-ItemProperty '" + REG + chr(92) + "0').ProcessorNameString",
    'topology_cim': ('Get-CimInstance Win32_Processor | Select-Object '
                     'Name,NumberOfCores,NumberOfLogicalProcessors,MaxClockSpeed | ConvertTo-Json -Compress'),
    'topology_env': '$env:NUMBER_OF_PROCESSORS',
    'logical_registry_count': "(Get-ChildItem '" + REG + "').Count",
    'power_plan': ('(Get-CimInstance -Namespace root/cimv2/power -ClassName Win32_PowerPlan '
                   '-Filter "IsActive=True").ElementName'),
    'os_build': 'Get-CimInstance Win32_OperatingSystem | Select-Object Caption,Version,BuildNumber | ConvertTo-Json -Compress',
    'thermal_throttle_hint': ('Get-CimInstance Win32_Processor | Select-Object '
                              'CurrentClockSpeed,MaxClockSpeed,LoadPercentage | ConvertTo-Json -Compress'),
}


def main() -> int:
    report = {'probed_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'purpose': 'M-03 residual: preserved commands and raw output for CPU topology and '
                         'benchmark context. Thread controls are set by the benchmark itself in '
                         'TASK-06 and recorded in its own run record.',
              'probes': {}}
    for name, command in PROBES.items():
        # Finding N-03: a nonzero exit was the only failure signal, so a query that
        # returned nothing while writing to stderr was reported as PASS.
        guarded = '$ErrorActionPreference = ' + chr(39) + 'Stop' + chr(39) + '; ' + command
        done = subprocess.run(['powershell.exe', '-NoProfile', '-NonInteractive', '-Command', guarded],
                              capture_output=True, text=True)
        stdout, stderr = done.stdout.strip(), done.stderr.strip()
        problems = []
        if done.returncode != 0:
            problems.append(f'exit {done.returncode}')
        if stderr:
            problems.append('stderr not empty')
        if not stdout:
            problems.append('stdout empty')
        report['probes'][name] = {
            'command': guarded, 'exit_code': done.returncode, 'stdout': stdout,
            'stderr': stderr[:500], 'problems': problems,
            'state': 'MEASURED' if not problems else 'UNAVAILABLE',
            'required': name in REQUIRED}
        print(f'{name}: {report["probes"][name]["state"]} | {stdout[:90]}')
    failed = [name for name, value in report['probes'].items()
              if value['problems'] and value['required']]
    unavailable = [name for name, value in report['probes'].items() if value['problems']]
    report['failed_required_probes'] = failed
    report['unavailable_probes'] = unavailable
    report['status'] = 'PASS' if not unavailable else ('PARTIAL' if not failed else 'FAIL')
    report['status_meaning'] = ('PASS only when every probe measured a value. PARTIAL means an '
                                'optional probe is honestly UNAVAILABLE. FAIL means a required '
                                'probe did not measure. A probe that returns nothing is never PASS.')
    check_output(authorized_root(), Path('provenance/environment/cpu_topology_probe.json')).write_text(
        json.dumps(report, indent=2) + chr(10), encoding='utf-8')
    print(json.dumps({'status': report['status'], 'failed_required': failed,
                      'unavailable': unavailable}))
    return 0 if report['status'] == 'PASS' else (1 if report['status'] == 'PARTIAL' else 2)


if __name__ == '__main__':
    raise SystemExit(main())
