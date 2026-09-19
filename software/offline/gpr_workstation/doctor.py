import importlib.util
import platform
import sys

CORE = ['numpy','scipy','matplotlib','yaml']
OPTIONAL = ['h5py','pandas','sklearn','pytest']


def _status(name):
    return importlib.util.find_spec(name) is not None


def main():
    print(f'Python: {sys.version.split()[0]} ({sys.executable})')
    print(f'Platform: {platform.platform()}')
    failures = 0
    for name in CORE:
        ok = _status(name)
        print(f'{"OK" if ok else "MISSING":7s} core     {name}')
        failures += int(not ok)
    for name in OPTIONAL:
        print(f'{"OK" if _status(name) else "MISSING":7s} optional {name}')
    if failures:
        print('Core dependencies are missing. Run ./setup_offline.sh from the FullStack root.')
        return 2
    print('Core offline processing environment is ready.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
