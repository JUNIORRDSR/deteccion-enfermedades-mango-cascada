"""The local-runtime checks of src/evaluation/authority.py that unit tests replace.

runtime_identity hashes every installed file (minutes), check_sources and check_loaded need a
committed checkout (a working tree under test is not), and fresh_bytecode would make every later
import of the test process compile from source. tests/test_authority_runtime.py tests all four
for real; check_startup stays real everywhere.
"""

from unittest import mock

from src.evaluation import authority

STUB = 'stub-runtime'
DRIVER = 'from tests import runtime_stub; runtime_stub.start(); '  # prefix for `python -c` drivers
_active = []


def start() -> None:
    for name, value in (('runtime_identity', lambda: STUB), ('check_runtime', lambda root: None),
                        ('check_sources', lambda: None),
                        ('check_loaded', lambda modules=None: None),
                        ('fresh_bytecode', lambda: None)):
        patcher = mock.patch.object(authority, name, value)
        patcher.start()
        _active.append(patcher)


def stop() -> None:
    while _active:
        _active.pop().stop()
