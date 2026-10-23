"""Record one Python replay command, its output, and observed resource use."""
import json
import platform
import resource
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]

if __name__ == "__main__":
    destination = PACKAGE / sys.argv[1]
    if destination.exists() or destination.parent != PACKAGE / "logs":
        raise SystemExit("Choose a new logs/<name>.json output")
    command = [sys.executable, *sys.argv[2:]]
    started = datetime.now(timezone.utc).isoformat()
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    tick = time.perf_counter()
    timed_out = False
    try:
        result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, timeout=600)
        code, stdout, stderr = result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired as error:
        timed_out = True
        code = None
        stdout = (error.stdout or b"").decode()
        stderr = (error.stderr or b"").decode()
    elapsed = time.perf_counter() - tick
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    record = {
        "command": ["python", *sys.argv[2:]],
        "cwd": "repository root",
        "started_at": started,
        "python": sys.version,
        "platform": platform.platform(),
        "returncode": code,
        "timed_out": timed_out,
        "timeout_seconds": 600,
        "wall_seconds_including_parent_capture": elapsed,
        "child_user_seconds": after.ru_utime - before.ru_utime,
        "child_system_seconds": after.ru_stime - before.ru_stime,
        "child_max_rss_kib_on_linux": after.ru_maxrss,
        "stdout": stdout,
        "stderr": stderr,
    }
    destination.parent.mkdir(exist_ok=True)
    destination.write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps({k: v for k, v in record.items() if k not in ("python", "platform")}))
    raise SystemExit(124 if timed_out else code)
