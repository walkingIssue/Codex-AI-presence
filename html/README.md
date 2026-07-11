# Codex AI Presence showcase

This directory is a static, dependency-free showcase page for the Codex AI Presence skill. It intentionally has no build step, so it can be previewed directly from a checkout:

```powershell
python -m http.server 8080 --directory html
```

Then open <http://localhost:8080>.

## Add recordings

Place finished videos in `media/videos/` using these names, or update the labels in `index.html`:

- `installation.mp4` — fresh checkout through first working response
- `orb-playback.mp4` — audio playback driving the strand orb
- `intel-arc.mp4` — Intel Arc DirectML setup and inference

Still images can go in `media/screenshots/`. The repository did not retain the old voice/orb debugging screenshots, so the first version uses designed media placeholders rather than unrelated local images. Replace those placeholders with verified screenshots or video poster frames when the recordings are ready.

The page is deliberately plain HTML, CSS, and JavaScript so it can also be hosted as a GitHub Pages site later without changing the showcase source.
