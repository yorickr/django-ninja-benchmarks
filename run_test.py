import os
import re
import subprocess
import time

CONCURRENT_FRAMEWORKS = [
    'drf_gunicorn',
    'ninja_gunicorn',
    'flask_marshmallow_uvicorn',
    'drf_uvicorn',
    'ninja_uvicorn',
    # 'ninja_asgi',
]


class FrameworkService:
    def __init__(self, name, workers=1):
        self.name = name
        self.workers = workers

    def __enter__(self):
        os.system(f'WORKERS={self.workers} docker compose up -d network_service')
        os.system(f'WORKERS={self.workers} docker compose up -d {self.name}')
        time.sleep(5)

    def __exit__(self, *a, **kw):
        os.system(f'WORKERS={self.workers} docker compose down')


def benchmark(url, concurency, count, payload=None):
    cmd = ['ab', '-c', f'{concurency}', '-n', f'{count}']
    if payload:
        cmd += ['-l', '-p', payload, '-T', 'application/json']
    cmd += [url]
    print('> ', ' '.join(cmd))
    result = subprocess.run(cmd, stdout=subprocess.PIPE)
    output = result.stdout.decode('utf-8')
    assert result.returncode == 0, output
    return parse_benchmark(output)


def parse_benchmark(output: str):
    # print(output)
    rps = re.findall(r'Requests per second: \s+(.*?)\s', output)[0]
    p50 = re.findall(r'\s+50%\s+(\d+)', output)[0]
    p99 = re.findall(r'\s+99%\s+(\d+)', output)[0]
    return (rps, p50, p99)
    # print()
    # re.findall(r'')


def preheat():
    benchmark('http://127.0.0.1:8000/api/create', 1, 5, 'payload.json')
    benchmark('http://127.0.0.1:8000/api/iojob', 1, 5)


def run_c1_test():
    return benchmark('http://127.0.0.1:8000/api/create', 1, 1000, 'payload.json')


WORKERS_CASES = [1, 2, 4, 8]


def test_concurrent(name):
    results = {}
    for workers in WORKERS_CASES:
        with FrameworkService(name, workers):
            preheat()
            results[workers] = run_c1_test()
    return results


def main():
    os.system(f'docker compose build')
    os.system(f'docker compose down')

    results = {}
    for framework in CONCURRENT_FRAMEWORKS:
        results[framework] = test_concurrent(framework)

    print('Framework               :', end='')
    for w in WORKERS_CASES:
        print(f'{w:>9}', end='')
    print('')
    for framework, results in sorted(results.items()):
        print(f'{framework:<23} :', end='')
        for w in WORKERS_CASES:
            print(f'{results[w][0]:>9}', end='')
        print('')


if __name__ == '__main__':
    main()
