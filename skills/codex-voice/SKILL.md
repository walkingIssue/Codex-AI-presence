---
name: codex-voice
description: Set up and control project-local Kokoro voice output and the optional WebGL Strand Orb for Codex, with per-session or project-wide scope. Use when the user asks to enable, disable, configure, install, troubleshoot, or speak Codex responses aloud, including CPU, NVIDIA CUDA, or Intel DirectML provider selection.
---

# Codex AI Presence

Use the bundled scripts from the active project directory. The setup is
project-local and does not modify other Python environments.

## Set up

If the active project has no `.codex-voice` directory, run:

```powershell
python "$HOME/.codex/skills/codex-voice/scripts/setup.py"
```

Use `--force` only when setup reports a different existing `.codex/hooks/speak.py`.
Use `--no-orb` when the machine should not install the optional Electron orb.

After setup, ask the user which voice scope they want before enabling it:

> Should voice apply only to this Codex session, or to all sessions in this project?

Use `session-on` for the current session or `project-on` for all sessions whose
rollout belongs to the active project. Do not silently choose project-wide
voice. If the user already specified a scope, use that choice without asking
again.

Provider setup options:

```powershell
python "$HOME/.codex/skills/codex-voice/scripts/setup.py" --cuda
python "$HOME/.codex/skills/codex-voice/scripts/setup.py" --directml
```

CPU is the validated baseline. The NVIDIA CUDA path uses a separate
`.cuda-venv`, `CUDAExecutionProvider`, and the base INT8 model; it is included
for NVIDIA users but is untested on the maintainer's hardware. The DirectML
path uses a separate `.dml-venv` and a generated local graph patch. The setup
pulls the maintained [Intel Arc Kokoro fork](https://github.com/walkingIssue/kokoro-onnx-intel-arc/tree/intel-arc-directml).
Do not describe the DirectML patch as an upstream Kokoro contribution yet.

## Controls

Run the requested operation:

```powershell
python "$HOME/.codex/skills/codex-voice/scripts/toggle.py" session-on
python "$HOME/.codex/skills/codex-voice/scripts/toggle.py" session-off
python "$HOME/.codex/skills/codex-voice/scripts/toggle.py" project-on
python "$HOME/.codex/skills/codex-voice/scripts/toggle.py" project-off
python "$HOME/.codex/skills/codex-voice/scripts/toggle.py" on             # alias for session-on
python "$HOME/.codex/skills/codex-voice/scripts/toggle.py" off            # alias for project-off
python "$HOME/.codex/skills/codex-voice/scripts/toggle.py" stream
python "$HOME/.codex/skills/codex-voice/scripts/toggle.py" quality
python "$HOME/.codex/skills/codex-voice/scripts/toggle.py" provider-cpu
python "$HOME/.codex/skills/codex-voice/scripts/toggle.py" provider-cuda
python "$HOME/.codex/skills/codex-voice/scripts/toggle.py" provider-directml
python "$HOME/.codex/skills/codex-voice/scripts/toggle.py" provider-status
python "$HOME/.codex/skills/codex-voice/scripts/toggle.py" progress-on
python "$HOME/.codex/skills/codex-voice/scripts/toggle.py" progress-off
python "$HOME/.codex/skills/codex-voice/scripts/toggle.py" orb-on
python "$HOME/.codex/skills/codex-voice/scripts/toggle.py" orb-off
python "$HOME/.codex/skills/codex-voice/scripts/toggle.py" status
```

Report the resulting state briefly. The skill controls future responses; it
does not speak the current response directly.

`session-on` registers the current `CODEX_THREAD_ID` in the project-local
`.codex-voice/sessions.json` file. `session-off` removes only the current
session. `project-on` is the explicit always-on mode for every matching
session in the project. The registration file is runtime state and is ignored
by the generated `.codex-voice/.gitignore`.

`stream` starts playback as Kokoro chunks arrive. `quality` buffers the full
waveform first. Visible progress commentary is optional and is spoken at half
volume; never speak hidden reasoning or raw tool output.

The watcher uses the persistent worker and the provider selected in the
project's `.codex-voice/provider` marker. Keep the base model and voice bundle
out of source control; setup downloads them locally.
