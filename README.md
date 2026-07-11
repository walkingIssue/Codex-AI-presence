# Codex AI Presence

A project-local Codex skill for fast Kokoro voice output, optional visible-progress speech, and the WebGL Strand Orb companion.

The repository deliberately does not contain the 88 MB Kokoro model or voice bundle. The setup script downloads them from the upstream `kokoro-onnx` model release when the skill is installed. See the [Kokoro ONNX repository](https://github.com/thewh1teagle/kokoro-onnx) and its [model release](https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0).

## Install the skill

In a Codex session, ask it to install:

```text
Install the `codex-voice` skill from walkingIssue/Codex-AI-presence, path skills/codex-voice.
```

Or use the preinstalled skill installer directly:

```powershell
python "$HOME/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py" `
  --repo walkingIssue/Codex-AI-presence `
  --path skills/codex-voice
```

## Set up a project

Run this from the project where voice should be enabled:

```powershell
python "$HOME/.codex/skills/codex-voice/scripts/setup.py" --enable
```

The setup creates an isolated project-local runtime, downloads the INT8 model and voices, installs a project-local Stop hook, and optionally installs the orb dependencies. It preserves an existing different `speak.py` by requiring `--force` before replacing it.

The machine needs `ffplay` on `PATH` for playback. Node.js/npm are optional unless the Strand Orb is wanted.

## Providers

CPU is the default and is the validated baseline.

For NVIDIA CUDA 12.x, use the optional CUDA runtime:

```powershell
python "$HOME/.codex/skills/codex-voice/scripts/setup.py" --cuda --enable
```

This installs `onnxruntime-gpu[cuda,cudnn]`, selects `CUDAExecutionProvider`, and keeps the CPU runtime available as a fallback. The CUDA path is included but untested on the maintainer’s hardware.

For the current Intel Arc/DirectML experiment:

```powershell
python "$HOME/.codex/skills/codex-voice/scripts/setup.py" --directml --enable
```

That installs the maintained [Intel Arc Kokoro fork](https://github.com/walkingIssue/kokoro-onnx-intel-arc/tree/intel-arc-directml), removes the CPU ONNX Runtime wheel from the DirectML environment, and generates the local graph patch. It is intentionally not an upstream Kokoro pull request yet.

## Controls

```powershell
python "$HOME/.codex/skills/codex-voice/scripts/toggle.py" status
python "$HOME/.codex/skills/codex-voice/scripts/toggle.py" on
python "$HOME/.codex/skills/codex-voice/scripts/toggle.py" off
python "$HOME/.codex/skills/codex-voice/scripts/toggle.py" stream
python "$HOME/.codex/skills/codex-voice/scripts/toggle.py" quality
python "$HOME/.codex/skills/codex-voice/scripts/toggle.py" provider-cpu
python "$HOME/.codex/skills/codex-voice/scripts/toggle.py" provider-cuda
python "$HOME/.codex/skills/codex-voice/scripts/toggle.py" provider-directml
python "$HOME/.codex/skills/codex-voice/scripts/toggle.py" progress-on
python "$HOME/.codex/skills/codex-voice/scripts/toggle.py" orb-on
```

The eventual Codex app-server bridge can feed public agent-message deltas into the same persistent voice worker and playback-synchronized orb.
