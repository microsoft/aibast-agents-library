"""
AutoResearch Agent — Autonomous LLM pretraining research.

Wraps karpathy/autoresearch: gives an AI agent a real LLM training setup
and lets it experiment autonomously. It modifies train.py, trains for
5 minutes, checks if val_bpb improved, keeps or discards, and repeats.

Supports local (NVIDIA GPU) and remote (SSH to GPU box) execution.
Configure via .env:
  AUTORESEARCH_DIR   — path to cloned autoresearch repo
  AUTORESEARCH_SSH   — optional SSH target (e.g. user@gpu-box)
  AUTORESEARCH_GPU   — GPU id (default: 0)
"""

import json
import os
import re
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

from agents.basic_agent import BasicAgent

_REPO_URL = "https://github.com/karpathy/autoresearch.git"
_DEFAULT_DIR = os.path.join(os.path.expanduser("~"), ".brainstem", "autoresearch")


class AutoResearchAgent(BasicAgent):
    def __init__(self):
        self.name = "AutoResearch"
        self.metadata = {
            "name": self.name,
            "description": (
                "Autonomous LLM pretraining research agent (karpathy/autoresearch). "
                "Runs experiments that modify train.py, train for 5 minutes, measure val_bpb, "
                "and keep or discard results. Can setup the repo, run single experiments, "
                "kick off autonomous loops, and report results."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "Action to perform.",
                        "enum": ["setup", "status", "baseline", "experiment", "results", "loop", "stop"]
                    },
                    "description": {
                        "type": "string",
                        "description": "For 'experiment': natural language description of what to try (e.g. 'increase learning rate to 0.04')."
                    },
                    "tag": {
                        "type": "string",
                        "description": "Experiment branch tag (e.g. 'mar14'). Used for 'setup' and 'loop'."
                    },
                    "num_experiments": {
                        "type": "integer",
                        "description": "For 'loop': number of experiments to run (default: 10)."
                    },
                    "num_shards": {
                        "type": "integer",
                        "description": "For 'setup': number of data shards to download (default: 10, -1 for all)."
                    }
                },
                "required": []
            }
        }
        super().__init__(name=self.name, metadata=self.metadata)

        self.repo_dir = os.getenv("AUTORESEARCH_DIR", _DEFAULT_DIR)
        self.ssh_target = os.getenv("AUTORESEARCH_SSH", "")
        self.gpu_id = os.getenv("AUTORESEARCH_GPU", "0")

    def perform(self, **kwargs):
        action = kwargs.get("action", "status")
        tag = kwargs.get("tag", "")
        description = kwargs.get("description", "")
        num_experiments = kwargs.get("num_experiments", 10)
        num_shards = kwargs.get("num_shards", 10)

        try:
            if action == "setup":
                return self._setup(tag, num_shards)
            elif action == "status":
                return self._status()
            elif action == "baseline":
                return self._run_baseline(tag)
            elif action == "experiment":
                return self._run_experiment(description)
            elif action == "results":
                return self._get_results()
            elif action == "loop":
                return self._run_loop(tag, num_experiments)
            elif action == "stop":
                return self._stop()
            else:
                return json.dumps({"status": "error", "message": f"Unknown action: {action}"})
        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)})

    # ── Shell execution (local or SSH) ──────────────────────────────────

    def _run(self, cmd, cwd=None, timeout=600):
        """Run a command locally or via SSH."""
        cwd = cwd or self.repo_dir
        if self.ssh_target:
            remote_cmd = f"cd {cwd} && {cmd}"
            full_cmd = ["ssh", "-o", "BatchMode=yes", self.ssh_target, remote_cmd]
        else:
            full_cmd = cmd
        result = subprocess.run(
            full_cmd,
            shell=not self.ssh_target,
            cwd=None if self.ssh_target else cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result

    def _run_check(self, cmd, cwd=None, timeout=600):
        """Run and raise on failure."""
        r = self._run(cmd, cwd, timeout)
        if r.returncode != 0:
            raise RuntimeError(f"Command failed: {cmd}\n{r.stderr[-500:]}")
        return r.stdout

    # ── Setup ───────────────────────────────────────────────────────────

    def _setup(self, tag="", num_shards=10):
        """Clone repo, install deps, download data, train tokenizer."""
        steps = []

        # Clone if missing
        if not os.path.exists(os.path.join(self.repo_dir, "train.py")):
            if self.ssh_target:
                self._run_check(f"git clone {_REPO_URL} {self.repo_dir}")
            else:
                os.makedirs(os.path.dirname(self.repo_dir), exist_ok=True)
                subprocess.run(
                    ["git", "clone", _REPO_URL, self.repo_dir],
                    capture_output=True, text=True, timeout=120
                )
            steps.append("Cloned autoresearch repo")
        else:
            self._run_check("git pull", timeout=30)
            steps.append("Repo already exists, pulled latest")

        # Install deps via uv
        try:
            self._run_check("uv sync", timeout=120)
            steps.append("Dependencies installed (uv sync)")
        except Exception as e:
            steps.append(f"uv sync warning: {str(e)[:200]}")

        # Prepare data
        shard_arg = f"--num-shards {num_shards}"
        try:
            r = self._run(f"uv run prepare.py {shard_arg}", timeout=600)
            if r.returncode == 0:
                steps.append(f"Data prepared ({num_shards} shards)")
            else:
                steps.append(f"Data prep warning: {r.stderr[-200:]}")
        except subprocess.TimeoutExpired:
            steps.append("Data prep timed out (may still be downloading)")

        # Create branch if tag provided
        if tag:
            branch = f"autoresearch/{tag}"
            self._run(f"git checkout -b {branch}", timeout=10)
            steps.append(f"Created branch: {branch}")

        # Initialize results.tsv
        tsv_path = os.path.join(self.repo_dir, "results.tsv")
        if not os.path.exists(tsv_path):
            with open(tsv_path, "w") as f:
                f.write("commit\tval_bpb\tmemory_gb\tstatus\tdescription\n")
            steps.append("Initialized results.tsv")

        return json.dumps({"status": "success", "steps": steps})

    # ── Status ──────────────────────────────────────────────────────────

    def _status(self):
        """Check current state of the autoresearch setup."""
        info = {"repo_dir": self.repo_dir, "ssh": self.ssh_target or "local"}

        if not os.path.exists(os.path.join(self.repo_dir, "train.py")):
            info["setup"] = False
            info["message"] = "Not set up yet. Use action='setup' first."
            return json.dumps(info)

        info["setup"] = True

        # Current branch
        r = self._run("git branch --show-current", timeout=5)
        info["branch"] = r.stdout.strip() if r.returncode == 0 else "unknown"

        # Results count
        tsv_path = os.path.join(self.repo_dir, "results.tsv")
        if os.path.exists(tsv_path):
            with open(tsv_path) as f:
                lines = [l for l in f.readlines() if l.strip() and not l.startswith("commit")]
            info["experiments"] = len(lines)
            if lines:
                last = lines[-1].split("\t")
                info["last_result"] = {
                    "val_bpb": last[1] if len(last) > 1 else "?",
                    "status": last[3] if len(last) > 3 else "?",
                    "description": last[4].strip() if len(last) > 4 else "?"
                }
        else:
            info["experiments"] = 0

        # Check GPU
        r = self._run("nvidia-smi --query-gpu=name,memory.total --format=csv,noheader", timeout=10)
        if r.returncode == 0:
            info["gpu"] = r.stdout.strip()
        else:
            info["gpu"] = "not detected"

        return json.dumps(info)

    # ── Training ────────────────────────────────────────────────────────

    def _run_training(self):
        """Run train.py and return parsed results."""
        r = self._run("uv run train.py > run.log 2>&1", timeout=600)

        # Parse results
        grep_r = self._run("grep '^val_bpb:\\|^peak_vram_mb:\\|^num_params_M:\\|^num_steps:\\|^total_tokens_M:' run.log", timeout=5)
        if grep_r.returncode != 0 or not grep_r.stdout.strip():
            # Crashed — get traceback
            tail_r = self._run("tail -n 50 run.log", timeout=5)
            return {
                "success": False,
                "crashed": True,
                "traceback": tail_r.stdout[-1000:] if tail_r.returncode == 0 else "Could not read log"
            }

        results = {}
        for line in grep_r.stdout.strip().split("\n"):
            if ":" in line:
                key, val = line.split(":", 1)
                results[key.strip()] = val.strip()

        return {
            "success": True,
            "val_bpb": float(results.get("val_bpb", 0)),
            "peak_vram_mb": float(results.get("peak_vram_mb", 0)),
            "num_params_M": results.get("num_params_M", "?"),
            "num_steps": results.get("num_steps", "?"),
            "total_tokens_M": results.get("total_tokens_M", "?"),
        }

    def _get_commit_hash(self):
        r = self._run("git rev-parse --short HEAD", timeout=5)
        return r.stdout.strip() if r.returncode == 0 else "unknown"

    def _log_result(self, commit, val_bpb, memory_gb, status, description):
        """Append a result to results.tsv."""
        tsv_path = os.path.join(self.repo_dir, "results.tsv")
        with open(tsv_path, "a") as f:
            f.write(f"{commit}\t{val_bpb:.6f}\t{memory_gb:.1f}\t{status}\t{description}\n")

    def _get_best_bpb(self):
        """Get the best (lowest) val_bpb from results.tsv."""
        tsv_path = os.path.join(self.repo_dir, "results.tsv")
        if not os.path.exists(tsv_path):
            return None
        best = None
        with open(tsv_path) as f:
            for line in f:
                if line.startswith("commit") or not line.strip():
                    continue
                parts = line.split("\t")
                if len(parts) >= 4 and parts[3].strip() == "keep":
                    bpb = float(parts[1])
                    if best is None or bpb < best:
                        best = bpb
        return best

    # ── Baseline ────────────────────────────────────────────────────────

    def _run_baseline(self, tag=""):
        """Run the unmodified train.py to establish baseline."""
        if tag:
            branch = f"autoresearch/{tag}"
            self._run(f"git checkout -b {branch} 2>/dev/null || git checkout {branch}", timeout=10)

        # Reset train.py to clean state
        self._run("git checkout -- train.py", timeout=5)
        self._run("git add -A && git commit -m 'baseline' --allow-empty", timeout=10)
        commit = self._get_commit_hash()

        result = self._run_training()
        if result["success"]:
            memory_gb = result["peak_vram_mb"] / 1024
            self._log_result(commit, result["val_bpb"], memory_gb, "keep", "baseline")
            return json.dumps({
                "status": "success",
                "action": "baseline",
                "val_bpb": result["val_bpb"],
                "memory_gb": round(memory_gb, 1),
                "commit": commit,
                "message": f"Baseline established: val_bpb={result['val_bpb']:.6f}"
            })
        else:
            self._log_result(commit, 0.0, 0.0, "crash", "baseline failed")
            return json.dumps({
                "status": "error",
                "action": "baseline",
                "message": "Baseline run crashed",
                "traceback": result.get("traceback", "")[:500]
            })

    # ── Single experiment ───────────────────────────────────────────────

    def _run_experiment(self, description):
        """Run a single experiment described in natural language.

        The brainstem LLM should have already modified train.py based on the
        description before calling this, OR this agent commits the current
        state of train.py and runs it.
        """
        if not description:
            return json.dumps({"status": "error", "message": "Provide a description of the experiment."})

        best_before = self._get_best_bpb()

        # Commit current train.py state
        self._run(f'git add train.py && git commit -m "{description[:80]}"', timeout=10)
        commit = self._get_commit_hash()

        # Train
        result = self._run_training()

        if not result["success"]:
            memory_gb = 0.0
            self._log_result(commit, 0.0, memory_gb, "crash", description[:200])
            # Revert
            self._run("git reset --hard HEAD~1", timeout=10)
            return json.dumps({
                "status": "crash",
                "commit": commit,
                "description": description,
                "traceback": result.get("traceback", "")[:500],
                "message": "Experiment crashed, reverted."
            })

        val_bpb = result["val_bpb"]
        memory_gb = result["peak_vram_mb"] / 1024
        improved = best_before is None or val_bpb < best_before

        if improved:
            status = "keep"
            self._log_result(commit, val_bpb, memory_gb, "keep", description[:200])
            message = f"Improved! val_bpb={val_bpb:.6f} (was {best_before:.6f})" if best_before else f"First result: val_bpb={val_bpb:.6f}"
        else:
            status = "discard"
            self._log_result(commit, val_bpb, memory_gb, "discard", description[:200])
            # Revert
            self._run("git reset --hard HEAD~1", timeout=10)
            message = f"No improvement: val_bpb={val_bpb:.6f} (best={best_before:.6f}), reverted."

        return json.dumps({
            "status": status,
            "val_bpb": val_bpb,
            "best_bpb": best_before,
            "memory_gb": round(memory_gb, 1),
            "commit": commit,
            "description": description,
            "message": message
        })

    # ── Autonomous loop ─────────────────────────────────────────────────

    def _run_loop(self, tag="", num_experiments=10):
        """Run multiple experiments autonomously.

        NOTE: This is a simplified loop that runs sequentially. The brainstem
        LLM generates experiment ideas and modifications to train.py. This
        agent handles the run/eval/keep-or-discard loop.

        For full autonomous operation, the LLM should call this agent
        repeatedly with action='experiment' and different descriptions.
        """
        results_summary = []

        # Ensure we have a baseline
        best = self._get_best_bpb()
        if best is None:
            baseline_result = json.loads(self._run_baseline(tag))
            if baseline_result.get("status") == "error":
                return json.dumps({
                    "status": "error",
                    "message": "Failed to establish baseline",
                    "detail": baseline_result
                })
            best = baseline_result.get("val_bpb", 0)
            results_summary.append({
                "experiment": 0,
                "description": "baseline",
                "val_bpb": best,
                "status": "keep"
            })

        return json.dumps({
            "status": "success",
            "message": (
                f"Baseline established (val_bpb={best:.6f}). "
                f"To run experiments, call AutoResearch with action='experiment' "
                f"and modify train.py between calls. The recommended flow:\n"
                f"1. Read train.py to understand current state\n"
                f"2. Make a targeted modification\n"
                f"3. Call AutoResearch(action='experiment', description='what you changed')\n"
                f"4. Review result and repeat\n\n"
                f"Refer to program.md for the full experiment protocol."
            ),
            "baseline_bpb": best,
            "experiments_so_far": results_summary
        })

    # ── Results ─────────────────────────────────────────────────────────

    def _get_results(self):
        """Return all experiment results from results.tsv."""
        tsv_path = os.path.join(self.repo_dir, "results.tsv")
        if not os.path.exists(tsv_path):
            return json.dumps({"status": "error", "message": "No results.tsv found. Run setup first."})

        experiments = []
        best_bpb = None
        with open(tsv_path) as f:
            for line in f:
                if line.startswith("commit") or not line.strip():
                    continue
                parts = line.strip().split("\t")
                if len(parts) >= 5:
                    entry = {
                        "commit": parts[0],
                        "val_bpb": parts[1],
                        "memory_gb": parts[2],
                        "status": parts[3],
                        "description": parts[4]
                    }
                    experiments.append(entry)
                    if parts[3] == "keep":
                        bpb = float(parts[1])
                        if best_bpb is None or bpb < best_bpb:
                            best_bpb = bpb

        return json.dumps({
            "status": "success",
            "total_experiments": len(experiments),
            "best_val_bpb": best_bpb,
            "experiments": experiments
        })

    # ── Stop ────────────────────────────────────────────────────────────

    def _stop(self):
        """Stop any running training process."""
        self._run("pkill -f 'train.py' || true", timeout=5)
        return json.dumps({"status": "success", "message": "Stopped any running training processes."})
