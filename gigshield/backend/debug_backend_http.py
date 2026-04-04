import subprocess
import time
import http.client
import sys

print('starting uvicorn')
p = subprocess.Popen(
    ['python', '-m', 'uvicorn', 'backend.main:app', '--host', '127.0.0.1', '--port', '8001', '--log-level', 'debug'],
    cwd=r'c:\Users\tejap\Downloads\GuideWire-main (1)\GuideWire-main\gigshield',
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
)
start = time.time()
started = False
while time.time() - start < 12:
    line = p.stdout.readline()
    if not line:
        break
    print('LOG:', line.strip())
    if 'Application startup complete.' in line:
        started = True
        break

if p.poll() is not None:
    print('process exited', p.returncode)
else:
    print('started', p.pid, 'ready=', started)
    try:
        conn = http.client.HTTPConnection('127.0.0.1', 8000, timeout=5)
        conn.request('GET', '/api/v1')
        r = conn.getresponse()
        print('status', r.status)
        print('body', r.read(200).decode('utf-8', errors='ignore'))
    except Exception as e:
        print('http error', repr(e))
    finally:
        conn.close()
    p.terminate()
    p.wait(timeout=5)
    print('terminated')
