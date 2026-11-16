#!/bin/bash
# Launch one full run under the supervisor once a local key file exists. The key is read from the file into
# the child's environment only; it is never printed or logged.
#   launch_run.sh <p1|p2> <log-name> <run command...>
# Key file: ~/.openrouter_key_<p1|p2> if present, else ~/.openrouter_key. Log: logs/<log-name>.log
set -u
proj=$1; name=$2; shift 2
cd "$(dirname "$0")" || exit 1
mkdir -p logs
echo "[$(date +%H:%M:%S)] $name: waiting for ~/.openrouter_key_$proj or ~/.openrouter_key ..."
until [ -s "$HOME/.openrouter_key_$proj" ] || [ -s "$HOME/.openrouter_key" ]; do sleep 3; done
key="$HOME/.openrouter_key_$proj"; [ -s "$key" ] || key="$HOME/.openrouter_key"
echo "[$(date +%H:%M:%S)] $name: key file found ($key); starting full run"
OPENROUTER_API_KEY="$(tr -d '[:space:]' < "$key")" caffeinate -i python3 supervise.py -- "$@" 2>&1 | tee -a "logs/$name.log"
