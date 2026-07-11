# Codex AI Presence

A project-local Codex skill for fast Kokoro voice output, optional visible-progress speech, and the WebGL Strand Orb companion.

The repository deliberately does not contain the 88 MB Kokoro model or voice bundle. The setup script downloads them from the upstream `kokoro-onnx` model release when the skill is installed. See the [Kokoro ONNX repository](https://github.com/thewh1teagle/kokoro-onnx) and its [model release](https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0).

## What the Strand Orb looks like

The Strand Orb is the optional transparent Electron/WebGL companion window for the local voice worker. It stays quietly visible while idle, with a dim luminous ring and a slow breathing pulse. During playback, the same audio stream drives the geometry: the strands brighten, become more angular, and deform in sync with Isabella's speech.

| Idle | Speaking |
| --- | --- |
| ![Strand Orb idle state](https://raw.githubusercontent.com/walkingIssue/Codex-AI-presence-pages/main/media/screenshots/orb-idle.png) | ![Strand Orb speaking state](https://raw.githubusercontent.com/walkingIssue/Codex-AI-presence-pages/main/media/screenshots/orb-speaking.png) |

The visual is intentionally small enough to sit beside an editor while still making the voice state legible at a glance. See the complete [Codex AI Presence showcase](https://walkingissue.github.io/Codex-AI-presence-pages/).

## Install the skill

In a Codex session, ask it to install:

```text
Install the `codex-voice` skill from walkingIssue/Codex-AI-presence, path skills/codex-voice.
```

Or use the preinstalled skill installer directly:

```powershell
python "$HOME/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py" `
  --repo walkingIssue/Codex-AI-presence `
  --path skills/codex-voice `
  --method git
```

## Set up a project

Run this from the project where voice should be enabled:

```powershell
python "$HOME/.codex/skills/codex-voice/scripts/setup.py"
```

The setup creates an isolated project-local runtime, downloads the INT8 model and voices, installs a project-local Stop hook, and optionally installs the orb dependencies. The Codex skill then asks whether voice should apply only to the current session or to all sessions in the project. It preserves an existing different `speak.py` by requiring `--force` before replacing it.

The machine needs `ffplay` on `PATH` for playback. Node.js/npm are optional unless the Strand Orb is wanted.

## Configuration

The project-local runtime exposes one complete configuration surface:

| Setting | Available values | Default |
| --- | --- | --- |
| Voice / timbre | Installed Kokoro voice ID, for example `bf_isabella` | `bf_isabella` |
| Speed | `0.5` to `2.0` | `1.08` |
| Playback | `stream` or `quality` | `stream` |
| Provider | `cpu`, `cuda`, or `directml` | `cpu` |
| Volume | `0` to `100` percent | `20` percent |
| Commentary volume | `0` to `100` percent of the main volume | `50` percent |
| Visible progress | `on` or `off` | `off` |
| Strand Orb | `on` or `off` | optional/off |
| Scope | `session`, `project`, or `off` | chosen when enabled |

Show the current matrix and effective values:

```powershell
python "$HOME/.codex/skills/codex-voice/scripts/configure.py" show
```

Walk through every setting interactively or apply selected values directly:

```powershell
python "$HOME/.codex/skills/codex-voice/scripts/configure.py" interactive
python "$HOME/.codex/skills/codex-voice/scripts/configure.py" set --voice bf_isabella --speed 1.08 --mode stream --volume 20 --commentary-volume 50
```

Visible progress commentary uses the configured commentary-volume ratio of the
main response volume. CUDA and DirectML selections are checked against their
installed project-local runtimes before they are activated.

## Providers

CPU is the default and is the validated baseline.

For NVIDIA CUDA 12.x, use the optional CUDA runtime:

```powershell
python "$HOME/.codex/skills/codex-voice/scripts/setup.py" --cuda
```

This installs `onnxruntime-gpu[cuda,cudnn]`, selects `CUDAExecutionProvider`, and keeps the CPU runtime available as a fallback. The CUDA path is included but untested on the maintainer’s hardware.

For the current Intel Arc/DirectML experiment:

```powershell
python "$HOME/.codex/skills/codex-voice/scripts/setup.py" --directml
```

That installs the maintained [Intel Arc Kokoro fork](https://github.com/walkingIssue/kokoro-onnx-intel-arc/tree/intel-arc-directml), removes the CPU ONNX Runtime wheel from the DirectML environment, and generates the local graph patch. It is intentionally not an upstream Kokoro pull request yet.

## Controls

```powershell
python "$HOME/.codex/skills/codex-voice/scripts/toggle.py" status
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
python "$HOME/.codex/skills/codex-voice/scripts/toggle.py" progress-on
python "$HOME/.codex/skills/codex-voice/scripts/toggle.py" orb-on
python "$HOME/.codex/skills/codex-voice/scripts/configure.py" show
```

`session-on` registers the current Codex thread in `.codex-voice/sessions.json`. `project-on` is the explicit always-on mode for all matching sessions in the project.

The eventual Codex app-server bridge can feed public agent-message deltas into the same persistent voice worker and playback-synchronized orb.
