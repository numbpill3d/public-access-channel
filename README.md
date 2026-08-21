# Public Access Channel

**A tiny website broadcasting network.** People publish short pieces of HTML to numbered channels. The homepage is a CRT television that rotates through them on its own — or you can tune it by hand.

Think public-access TV, except each program is somebody's webpage.

**▶ Watch it live: https://numbpill3d.github.io/public-access-channel/**

![The set tuned to CH02 — JOURNALS](screenshot.png)

---

## Run it locally

Everything is static. There is no build step, no package manager, and no backend.

```bash
git clone https://github.com/numbpill3d/public-access-channel.git
cd public-access-channel
python3 -m http.server 8000
```

Then open <http://localhost:8000>.

You can also just open `index.html` straight from disk (`xdg-open index.html`). The only external dependencies are Three.js and three webfonts, both from CDNs — offline, the set still works and simply falls back to your system monospace.

## Working the set

It's a television, so you operate it like one. The whole cabinet is live.

| Control | What it does |
|---|---|
| **CH −** / **CH +** buttons, or `←` `→` `[` `]` | Tune down / up a channel |
| **Preset** buttons (02, 03, 04, 07, 11, 404) | Jump straight to a channel |
| **POWER**, or `P` | Switch the set off and on — tube collapse, degauss, and warm-up included |
| **VOLUME** knob — drag it, scroll it, or focus it and use `↑` `↓` | Master volume. Starts at **MUTE** |
| `M` | Mute / unmute |
| **FLYBACK 15.7kHz** switch | Adds the high whine a real CRT makes. Off by default — see below |
| Nothing at all | The set tunes itself |

**Timing** — the set changes channel every **4 minutes**. Inside a channel with more than one program, it moves to the next program every **40 seconds**. Every switch is covered by **3 seconds of static**, the way a real tuner would.

## The set itself

The television isn't a picture of a television. It's built out of the page.

**The tube** is a true 4:3 rectangle with the uneven corner radius of curved glass, and the picture carries the artifacts a real one would: an RGB **shadow mask** at the sub-pixel level, **scanlines** with a slow mains flicker, a **bright band rolling** up a slightly out-of-sync picture, **corner vignetting**, **phosphor bloom** on every glyph, and a **specular reflection** across the faceplate. Switch it off and the image **collapses to a white line, then a dot**.

**Between channels** the tuner loses its grip: the picture **tears sideways**, real animated **snow** fills the tube, and the channel badge flashes in the corner as it locks on.

**Sound** is synthesized live with the Web Audio API — there are no audio files in this repo. Turning the volume up gets you the carrier hiss of a live tube, a burst of static across every channel change, a two-tone lock confirmation, the mechanical clunk of the power switch, the wobbling hum of the **degaussing coil** at power-on, and a click with real body under each button.

> **About the flyback switch.** A working CRT emits a 15.7kHz tone from its flyback transformer. Plenty of people genuinely hear it, and plenty of those find it painful. It's reproduced here accurately, which is exactly why it is **off by default, very quiet, and behind its own switch** rather than part of the normal sound.

Audio stays muted until you turn the knob — browsers require a deliberate gesture before any page may make sound. Everything degrades cleanly: no Web Audio support means a silent but fully working television, and `prefers-reduced-motion` stops the rolling band and the tearing.

## The channels

Six channels, currently carrying 11 programs between them.

| Channel | Name | Carries |
|---|---|---|
| **CH02** | JOURNALS | Personal logs, diary entries, thoughts in the dark |
| **CH03** | ART | Visual works, pixel art, glitch compositions |
| **CH04** | COMPUTERS | Code snippets, terminal output, ASCII and text-mode art |
| **CH07** | PERSONAL | Link pages, bios, personal spaces |
| **CH11** | UNKNOWN | Experimental, uncategorized, anomalous broadcasts |
| **CH404** | TEST | Test pattern and debugging |

CH03 and CH11 carry the **NHI pet** — a low-poly Three.js entity that floats, tracks your cursor with three eye-sensors, cycles moods when clicked, and gets hungry if you leave it alone.

## Broadcasting something

**The easy way.** Open [`public_access_submit.html`](public_access_submit.html) in a browser. Fill in a title, your handle, a channel, and your HTML — it previews live and copies the finished JSON to your clipboard. Paste that into the right channel's `programs` array in `public_access_channels.js`.

**By hand.** Add an object to the `programs` array of any channel in `public_access_channels.js`:

```javascript
{
    title: "YOUR PROGRAM TITLE",
    author: "your-handle",
    duration: 15,  // seconds on screen, roughly
    html: '<div style="color:#fff">Your HTML goes here</div>'
}
```

A few things worth knowing:

- Your HTML is injected into the tube, so it inherits the CRT styling — scanlines, phosphor bloom, and all. Inline styles override it.
- Every effect layer is `pointer-events: none`, so interactive programs still receive clicks.
- Keep it short. This is a TV spot, not a homepage.
- `duration` is a hint — the rotation is what actually drives the pacing.

Then open `index.html` to check it, and send a pull request. If PRs aren't your thing, open an issue with your program pasted in and it'll get added.

## Deploying your own

**GitHub Pages** — fork, then **Settings → Pages → Deploy from a branch → `main` / `/ (root)`**. Because the entry point is `index.html`, it serves at the bare URL with no further configuration. Three.js comes from a CDN, so nothing needs bundling.

**Neocities** — upload the files to your site root. `index.html` becomes your homepage automatically:

```bash
npm install -g neocities
neocities login
neocities upload index.html public_access_channels.js public_access_submit.html \
                nhi_pet.js nhi_pet_widget.html nhi_pet_demo.html
```

**Anything else** — it's a folder of static files. Netlify, Cloudflare Pages, an nginx container, a USB stick. All the same.

## Files

| File | What it is |
|---|---|
| `index.html` | The whole television — cabinet, tube, effects, sound, and channel rotation |
| `public_access_channels.js` | **All channel and program content.** This is the file you edit |
| `public_access_submit.html` | Submission form with live preview and JSON export |
| `nhi_pet.js` | The NHI pet, as a reusable module |
| `nhi_pet_widget.html` | Standalone self-contained pet widget |
| `nhi_pet_demo.html` | Minimal demo page for the pet |

## Type and finish

Three faces, on one rule — **displays glow, plastic is printed, people write by hand**:

| Face | Used for |
|---|---|
| **VT323** | Anything that is a display: the picture, the channel badge, the panel readout, the now-playing plate. It's a true monospace, so ASCII-art programs stay aligned |
| **Silkscreen** | Anything screen-printed on the cabinet: the badge, the panel labels, the button faces |
| **Permanent Marker** | The masking-tape labels somebody stuck on the set |

Channel numbers are the one thing on the panel that must never be ambiguous, so they use VT323 rather than Silkscreen — a pixel `4` with an open top turns `404` into guesswork.

The finish: dark moulded plastic with scuffs and a scratched top edge, one strip of dark woodgrain veneer across the brow, a lit power lamp, a green panel readout, and a palette of purple `#8b008b`, magenta `#ff69b4`, green `#0f0`, and red `#ff0000`.

---

*This repository also contains `neocities_sort.py`, an unrelated tool for bulk-organizing files on a Neocities site — see [`README-neocities-sorter.md`](README-neocities-sorter.md).*
