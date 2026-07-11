"""Toggle the project-local Codex Kokoro voice hook."""

from __future__ import annotations

import argparse
import os
import signal
import subprocess
import sys
import time
from pathlib import Path


WATCHER_SCRIPT = Path(__file__).with_name("watcher.py")


def find_voice_root() -> Path | None:
    current = Path.cwd().resolve()
    candidates = (current, *current.parents)
    for candidate in candidates:
        voice_root = candidate / ".codex-voice"
        if voice_root.is_dir():
            return voice_root
    return None


def watcher_pid_path(voice_root: Path) -> Path:
    return voice_root / "watcher.pid"


def watcher_pid(voice_root: Path) -> int | None:
    try:
        return int(watcher_pid_path(voice_root).read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return None


def watcher_is_running(voice_root: Path) -> bool:
    pid = watcher_pid(voice_root)
    if pid is None:
        return False
    if os.name == "nt":
        try:
            result = subprocess.run(
                ["tasklist", "/FI", f"PID eq {pid}", "/NH"],
                capture_output=True,
                text=True,
                check=False,
            )
            return str(pid) in result.stdout
        except OSError:
            return False
    try:
        os.kill(pid, 0)
    except PermissionError:
        return True
    except OSError:
        return False
    return True


def orb_pid(voice_root: Path) -> int | None:
    try:
        return int((voice_root / "orb" / "orb.pid").read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return None


def orb_is_running(voice_root: Path) -> bool:
    pid = orb_pid(voice_root)
    if pid is None:
        return False
    if os.name == "nt":
        try:
            result = subprocess.run(
                ["tasklist", "/FI", f"PID eq {pid}", "/NH"],
                capture_output=True,
                text=True,
                check=False,
            )
            return str(pid) in result.stdout
        except OSError:
            return False
    try:
        os.kill(pid, 0)
    except PermissionError:
        return True
    except OSError:
        return False
    return True


def run_orb_script(voice_root: Path, name: str) -> None:
    script = voice_root / "orb" / name
    if not script.is_file():
        raise FileNotFoundError(script)
    subprocess.run(
        [
            "powershell.exe",
            "-NoProfile",
            "-NonInteractive",
            "-WindowStyle",
            "Hidden",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(script),
        ],
        cwd=str(voice_root),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )


def start_watcher(voice_root: Path) -> None:
    if watcher_is_running(voice_root):
        return
    project_root = voice_root.parent
    arguments = [
        str(WATCHER_SCRIPT),
        "--project-root",
        str(project_root),
        "--voice-root",
        str(voice_root),
        "--start-time",
        str(time.time()),
    ]

    def powershell_quote(value: str) -> str:
        return "'" + value.replace("'", "''") + "'"

    argument_list = " ".join(
        '"' + value.replace('"', '\\"') + '"' for value in arguments
    )
    command = (
        "$process = Start-Process "
        f"-FilePath {powershell_quote(sys.executable)} "
        f"-ArgumentList {powershell_quote(argument_list)} "
        f"-WorkingDirectory {powershell_quote(str(project_root))} "
        "-WindowStyle Hidden -PassThru; "
        "Write-Output $process.Id"
    )
    result = subprocess.run(
        ["powershell.exe", "-NoProfile", "-NonInteractive", "-WindowStyle", "Hidden", "-Command", command],
        capture_output=True,
        text=True,
        check=False,
    )
    pid = next((line.strip() for line in reversed(result.stdout.splitlines()) if line.strip().isdigit()), None)
    if pid is not None:
        watcher_pid_path(voice_root).write_text(pid, encoding="utf-8")


def stop_watcher(voice_root: Path) -> None:
    pid = watcher_pid(voice_root)
    if pid is None:
        return
    if os.name == "nt":
        try:
            subprocess.run(
                ["taskkill", "/PID", str(pid), "/T", "/F"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
        except OSError:
            pass
        return
    try:
        os.kill(pid, signal.SIGTERM)
    except OSError:
        pass


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "operation",
        choices=(
            "on",
            "off",
            "stream",
            "quality",
            "provider-cpu",
            "provider-directml",
            "provider-cuda",
            "provider-status",
            "progress-on",
            "progress-off",
            "orb-on",
            "orb-off",
            "orb-status",
            "status",
        ),
    )
    args = parser.parse_args()

    voice_root = find_voice_root()
    if voice_root is None:
        print("No project-local .codex-voice directory was found.", file=sys.stderr)
        return 2

    marker = voice_root / "enabled"
    if args.operation == "on":
        marker.write_text("on\n", encoding="utf-8")
        start_watcher(voice_root)
        print(f"Codex voice: on ({voice_root})")
        return 0

    if args.operation == "off":
        marker.unlink(missing_ok=True)
        stop_watcher(voice_root)
        print(f"Codex voice: off ({voice_root})")
        return 0

    if args.operation in {"stream", "quality"}:
        (voice_root / "mode").write_text(f"{args.operation}\n", encoding="utf-8")
        print(f"Codex voice mode: {args.operation} ({voice_root})")
        return 0

    if args.operation in {"provider-cpu", "provider-directml", "provider-cuda"}:
        provider = (
            "directml"
            if args.operation == "provider-directml"
            else "cuda"
            if args.operation == "provider-cuda"
            else "cpu"
        )
        if provider == "directml":
            dml_python = voice_root / ".dml-venv" / "Scripts" / "python.exe"
            dml_model = voice_root / "gpu_patch" / "kokoro-v1.0.int8.dml-conv2d.onnx"
            if not dml_python.is_file() or not dml_model.is_file():
                print(
                    "DirectML is not ready: expected .dml-venv and the patched graph under gpu_patch.",
                    file=sys.stderr,
                )
                return 2
        if provider == "cuda":
            cuda_python = voice_root / ".cuda-venv" / "Scripts" / "python.exe"
            model = voice_root / "kokoro-v1.0.int8.onnx"
            if not cuda_python.is_file() or not model.is_file():
                print(
                    "CUDA is not ready: expected .cuda-venv and the base Kokoro model.",
                    file=sys.stderr,
                )
                return 2
        (voice_root / "provider").write_text(f"{provider}\n", encoding="utf-8")
        if watcher_is_running(voice_root):
            stop_watcher(voice_root)
            time.sleep(0.5)
            start_watcher(voice_root)
        print(f"Codex voice provider: {provider} ({voice_root})")
        return 0

    if args.operation == "provider-status":
        try:
            provider = (voice_root / "provider").read_text(encoding="utf-8").strip().lower()
        except OSError:
            provider = "cpu"
        if provider in {"cuda", "cudaexecutionprovider", "nvidia", "nvidia-cuda"}:
            provider = "cuda"
        elif provider in {"directml", "dml", "gpu"}:
            provider = "directml"
        else:
            provider = "cpu"
        print(f"Codex voice provider: {provider} ({voice_root})")
        return 0

    if args.operation in {"progress-on", "progress-off"}:
        progress_path = voice_root / "progress"
        if args.operation == "progress-on":
            progress_path.write_text("on\n", encoding="utf-8")
        else:
            progress_path.unlink(missing_ok=True)
        state = "on" if args.operation == "progress-on" else "off"
        print(f"Codex visible progress voice: {state} ({voice_root})")
        return 0

    if args.operation in {"orb-on", "orb-off"}:
        marker = voice_root / "orb.enabled"
        if args.operation == "orb-on":
            marker.write_text("on\n", encoding="utf-8")
            run_orb_script(voice_root, "start_orb.ps1")
            print(f"Codex Strand Orb: on ({voice_root})")
        else:
            marker.unlink(missing_ok=True)
            run_orb_script(voice_root, "stop_orb.ps1")
            print(f"Codex Strand Orb: off ({voice_root})")
        return 0

    if args.operation == "orb-status":
        marker = voice_root / "orb.enabled"
        enabled = marker.is_file() and marker.read_text(encoding="utf-8").strip().lower() in {
            "1",
            "true",
            "on",
            "enabled",
        }
        print(
            f"Codex Strand Orb: {'on' if enabled else 'off'} "
            f"({voice_root}; window: {'running' if orb_is_running(voice_root) else 'stopped'})"
        )
        return 0

    enabled = marker.is_file() and marker.read_text(encoding="utf-8").strip().lower() in {
        "1",
        "true",
        "on",
        "enabled",
    }
    watcher = "running" if watcher_is_running(voice_root) else "stopped"
    try:
        mode = (voice_root / "mode").read_text(encoding="utf-8").strip().lower()
    except OSError:
        mode = "stream"
    try:
        speed = (voice_root / "speed").read_text(encoding="utf-8").strip()
    except OSError:
        speed = "1.0"
    try:
        progress = (voice_root / "progress").read_text(encoding="utf-8").strip().lower()
    except OSError:
        progress = "off"
    progress = "on" if progress in {"1", "true", "on", "enabled"} else "off"
    try:
        provider = (voice_root / "provider").read_text(encoding="utf-8").strip().lower()
    except OSError:
        provider = "cpu"
    if provider in {"cuda", "cudaexecutionprovider", "nvidia", "nvidia-cuda"}:
        provider = "cuda"
    elif provider in {"directml", "dml", "gpu"}:
        provider = "directml"
    else:
        provider = "cpu"
    print(
        f"Codex voice: {'on' if enabled else 'off'} "
        f"({voice_root}; mode: {mode}; speed: {speed}; progress: {progress}; "
        f"provider: {provider}; desktop watcher: {watcher})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
