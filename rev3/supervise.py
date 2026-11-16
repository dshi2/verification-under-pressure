"""Keep a run going until it completes: resume automatically after transient stops, stop on anything that
needs a person. Stdlib only; identical copy in both repos.

  python3 supervise.py [--max-resumes 200] -- python3 run_p2.py --config C.json ... --run-dir runs/X

The first launch passes the command as given (adding --resume if runs/X already holds a journal); every
later launch adds --resume, which the runner refuses unless config, stimuli/items, design and repeats are
identical, so a resume can never change the experiment. Counted results are journaled once per key, so a
resume never duplicates an observation.

Resumes (wait 60 s, doubling to 10 min) when the runner
- halted on too many transient aborts (rate limits, 5xx, timeouts, network loss), or
- exited without writing a summary after running at least 2 minutes (crash, OOM, killed process); a
  runner that refuses to start does so within seconds.
Stops, with a message, when
- the run is complete, or
- PAUSE file / Ctrl-C (a person stopped it), HTTP 401/402/403 (key or credit), terminal-failure rate
  above halt_error_rate (systematic error), spend cap, disk or journal problems, or
- the runner refused to start (lock held by a live runner, changed design, corrupt journal, no key), or
- --max-resumes is reached, or
- no-progress circuit breaker: 3 consecutive resume cycles add no completed stage key (unique journaled
  results), so a persistent defect cannot crash-loop unattended.
"complete" means every planned task ran; it is NOT a data-quality verdict. Run the analysis checks after.
"""
import argparse
import json
import os
import subprocess
import sys
import time

RESUMABLE = ("too many tasks aborted on transient errors",)
NO_PROGRESS_LIMIT = 3


def done_count(run_dir):
    """Unique journaled stage results, read from the journal (works whether or not a summary was written)."""
    seen = set()
    try:
        with open(os.path.join(run_dir, "journal.jsonl")) as f:
            for line in f:
                if '"type": "result"' in line:
                    try:
                        seen.add(json.loads(line)["key"])
                    except (ValueError, KeyError):
                        pass  # torn last line: the runner repairs it on resume
    except OSError:
        pass
    return len(seen)


def log(msg):
    print(f"[supervise {time.strftime('%H:%M:%S')}] {msg}", file=sys.stderr, flush=True)


def mtime(path):
    try:
        return os.path.getmtime(path)
    except OSError:
        return 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-resumes", type=int, default=200)
    ap.add_argument("--wait", type=float, default=60.0, help="first wait before a resume, seconds")
    ap.add_argument("cmd", nargs=argparse.REMAINDER)
    a = ap.parse_args()
    cmd = a.cmd[1:] if a.cmd[:1] == ["--"] else a.cmd
    if "--run-dir" not in cmd:
        ap.error("the run command needs --run-dir")
    run_dir = cmd[cmd.index("--run-dir") + 1]
    journal, summary_path = os.path.join(run_dir, "journal.jsonl"), os.path.join(run_dir, "summary.json")
    wait, prev_done, stalls = a.wait, None, 0
    for n in range(a.max_resumes + 1):
        resume = os.path.exists(journal)
        launch = cmd + (["--resume"] if resume and "--resume" not in cmd else [])
        log(("resume %d" % n if resume else "start") + ": " + " ".join(launch))
        t0 = time.time()
        try:
            code = subprocess.call(launch)
        except KeyboardInterrupt:
            log("Ctrl-C: stopped by a person; resume with the same command")
            return 130
        wrote_summary = mtime(summary_path) >= t0
        s = {}
        if wrote_summary:
            with open(summary_path) as f:
                s = json.load(f)
        if s.get("complete"):
            log("run complete")
            return 0
        if os.path.exists(os.path.join(run_dir, "PAUSE")):
            log("PAUSE file present: stopped by a person; resume with the same command")
            return 3
        reason = (s.get("stop_info") or {}).get("reason")
        if wrote_summary:
            if reason not in RESUMABLE:
                log(f"stopped and needs a person: {reason or 'incomplete with no stop reason'} (exit {code}); "
                    f"inspect, then rerun the same command")
                return 4
            log(f"transient stop ({reason}); {s.get('calls_pending')} calls pending")
        elif time.time() - t0 > 120:
            log(f"runner exited (code {code}) without a summary after {time.time() - t0:.0f} s: treating as a crash")
        else:
            log(f"runner refused to start or failed before any progress (exit {code}); fix, then rerun")
            return 5
        done = done_count(run_dir)
        progressed = prev_done is None or done > prev_done
        stalls = 0 if progressed else stalls + 1
        prev_done = done
        if stalls >= NO_PROGRESS_LIMIT:
            log(f"no-progress circuit breaker: {stalls} consecutive cycles added no completed stage "
                f"({done} done); inspect before rerunning the same command")
            return 7
        if n == a.max_resumes:
            break
        log(f"waiting {wait:.0f} s before resuming")
        try:
            time.sleep(wait)
        except KeyboardInterrupt:
            log("Ctrl-C during wait: stopped; resume with the same command")
            return 130
        wait = a.wait if progressed else min(wait * 2, 600.0)  # back off only while nothing new completes
    log(f"max resumes ({a.max_resumes}) reached; rerun the same command to continue")
    return 6


if __name__ == "__main__":
    sys.exit(main())
