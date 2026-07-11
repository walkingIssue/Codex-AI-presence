# Codex AI Presence showcase

This directory is a static, dependency-free showcase page for the Codex AI Presence skill. It intentionally has no build step, so it can be previewed directly from a checkout:

```powershell
python -m http.server 8080 --directory html
```

Then open <http://localhost:8080>.

## Add recordings

The showcase currently embeds these compressed recordings from `media/videos/`:

- `installation.mp4` — fresh checkout through first working response
- `voice-swap.mp4` — changing the local Kokoro voice
- `other-instance.mp4` — the presence workflow in another Codex instance

Replace or add recordings using the same names, or update the `<source>` paths in `index.html`.

Verified orb captures live in `media/screenshots/`: `orb-idle.png` shows the quiet baseline and `orb-speaking.png` shows the brighter geometric response during Isabella playback. Add further stills there as the showcase grows.

The page is deliberately plain HTML, CSS, and JavaScript so it can also be hosted as a GitHub Pages site later without changing the showcase source.
