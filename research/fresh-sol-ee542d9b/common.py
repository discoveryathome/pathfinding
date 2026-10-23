"""Local experiment bookkeeping; optimizers and the separate audit stay apart."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
sys.path.insert(0, str(ROOT / "src"))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as handle:
        handle.write(json.dumps(data, indent=2) + "\n")


def protocol():
    return json.loads((PACKAGE / "protocol.json").read_text())


def source_paths(plan):
    prefix = str(PACKAGE.relative_to(ROOT)) + "/"
    return sorted({prefix + name for name in ("common.py", "inputs.py", "run_native.py",
                                              "run_repair.py", "sol_repair.py", "protocol.json")}
                  | {"src/model.py", "src/repair.py", "src/repair_round2.py", "src/verify.py"}
                  | {case["map"] for case in plan["cases"]})


def source_identity(plan):
    paths = source_paths(plan)
    tracked = subprocess.check_output(["git", "ls-files", "--", *paths], cwd=ROOT, text=True).splitlines()
    if set(tracked) != set(paths):
        raise ValueError("Commit every producer source and input map before running")
    subprocess.run(["git", "diff", "--exit-code", "HEAD", "--", *paths], cwd=ROOT, check=True,
                   stdout=subprocess.DEVNULL)
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    hashes = {path: sha(ROOT / path) for path in paths}
    if sha(PACKAGE / "sol_repair.py") != plan["policy_sha256"]:
        raise ValueError("Frozen policy changed")
    for case in plan["cases"]:
        if hashes[case["map"]] != case["map_sha256"]:
            raise ValueError("Map binding changed")
    return {"code_commit": commit, "source_sha256": hashes}


def remaining_seconds(plan):
    limit = datetime.fromisoformat(plan["caps"]["research_cutoff_utc"])
    return (limit - datetime.now(timezone.utc)).total_seconds()


def check_limits(plan):
    if remaining_seconds(plan) <= 0:
        raise TimeoutError("Research cutoff reached")
    size = sum(path.stat().st_size for path in PACKAGE.rglob("*") if path.is_file())
    if size > plan["caps"]["package_mib"] * 1024 ** 2:
        raise RuntimeError("Package disk cap reached")


def run_process(command, timeout, memory_mib):
    def memory_limit():
        resource.setrlimit(resource.RLIMIT_AS, (memory_mib * 1024 ** 2,) * 2)

    started = time.perf_counter()
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    child = subprocess.Popen(command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             text=True, start_new_session=True, preexec_fn=memory_limit)
    try:
        out, err = child.communicate(timeout=timeout)
        status = "complete" if child.returncode == 0 else "failed"
    except subprocess.TimeoutExpired:
        os.killpg(child.pid, signal.SIGKILL)
        out, err = child.communicate()
        status = "timeout"
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    return {"command": command, "status": status, "returncode": child.returncode,
            "stdout": out, "stderr": err, "wall_seconds": time.perf_counter() - started,
            "child_user_cpu_seconds": after.ru_utime - before.ru_utime,
            "child_system_cpu_seconds": after.ru_stime - before.ru_stime,
            "max_child_rss_kib_on_linux_so_far": after.ru_maxrss,
            "external_timeout_seconds": timeout, "address_space_mib": memory_mib}


def load_inputs():
    return json.loads((PACKAGE / "inputs.json").read_text())


def find_case(plan, case_id):
    return next(case for case in plan["cases"] if case["id"] == case_id)
