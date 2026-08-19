# Public Access Channel — Tiny Website Broadcasting Network

[![Neocities](https://img.shields.io/badge/neocities-000000?style=for-the-badge&logo=digitalocean&labelColor=252526&color=000000&label=)](https://nolove.neocities.org)
[![Made with JavaScript](https://img.shields.io/badge/-Three.js-000000?style=for-the-badge&logo=three.js&labelColor=0c0c0c&color=000000)](https://threejs.org)
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github)](https://github.com/numbpill3d/public-access-channel)

A tiny website broadcasting network where people publish short pieces of HTML to numbered channels. The homepage TV rotates through channels every few minutes, and visitors can tune manually.

Think public-access television, except each program is somebody's webpage.

**Repository**: `https://github.com/numbpill3d/public-access-channel`

## Quick Start — Get It Running

### Option 1: Run Locally (Fastest)
```bash
# Clone or download
git clone https://github.com/numbpill3d/public-access-channel.git
cd public-access-channel

# Open in your browser (no server needed — it's all static)
# Just double-click the file:
open public_access_tv.html      # macOS
xdg-open public_access_tv.html  # Linux
start public_access_tv.html     # Windows
```

Or, if you have Python installed:
```bash
python3 -m http.server 8000
# Then visit: http://localhost:8000/public_access_tv.html
```

### Option 2: GitHub Pages
1. Fork this repo (click the **Fork** button at the top of [the repo](https://github.com/numbpill3d/public-access-channel))
2. Go to **Settings → Pages**
3. Under "Build and deployment", select **Deploy from a branch**
4. Choose branch: `main`, folder: `/ (root)`
5. Save — your TV will be live at `https://your-username.github.io/public-access-channel/public_access_tv.html`

> **Note**: Three.js loads from CDN, so GitHub Pages works without any config changes.

### Option 3: Neocities (Recommended for this project)
```bash
# Install neocities CLI if you haven't already
npm install -g neocities

# Login to your Neocities account
neocities login

# Upload all files
neocities upload public_access_tv.html public_access_channels.js public_access_submit.html nhi_pet.js nhi_pet_widget.html nhi_pet_demo.html

# Optionally, make the TV your homepage
neocities upload --force public_access_tv.html:index.html
```

Or use the web dashboard at `https://neocities.org/site/YOUR-SITE-NAME`.

### Option 4: Direct Download
- Download the [latest release ZIP](https://github.com/numbpill3d/public-access-channel/archive/refs/heads/main.zip)
- Extract and open `public_access_tv.html` in any browser

## Channel Directory

| Channel | Name | Theme |
|---------|------|-------|
| **CH02** | JOURNALS | Personal logs, diary entries, thoughts in the dark |
| **CH03** | ART | Visual works, pixel art, glitch compositions |
| **CH04** | COMPUTERS | Code snippets, terminal output, ASCII |
| **CH07** | PERSONAL | About pages, bios, link collections |
| **CH11** | UNKNOWN | Experimental, uncategorized, weird |
| **CH404** | TEST | Test pattern and debugging |

## Files

| File | Purpose |
|------|---------|
| `public_access_tv.html` | **Main page** — the TV with channel rotation, CRT aesthetic, and navigation |
| `public_access_channels.js` | **Channel data** — all programs organized by channel (edit this to add content) |
| `public_access_submit.html` | **Submission form** — submit form with live preview (copies JSON to clipboard) |
| `nhi_pet.js` | NHI digital pet module (used as living content on ART/UNKNOWN channels) |
| `nhi_pet_widget.html` | Standalone NHI pet widget (self-contained) |

## How It Works

### Auto-Rotation
- The TV automatically switches to a new channel every **4 minutes**
- Within multi-program channels, the current program rotates every **40 seconds**
- Between switches: **3 seconds of static** (CRT-style effect)

### Manual Navigation
- **[CHANNEL -]** / **[CHANNEL +]** buttons
- Click the **navigation dots** below the screen
- **Keyboard**: `[` / `]` or `←` / `→` arrows

### Submission
1. Go to `public_access_submit.html`
2. Fill in title, author, select a channel, and paste your HTML
3. The form copies the JSON to your clipboard
4. Add the JSON to the matching channel's `programs` array in `public_access_channels.js`

Or directly edit `public_access_channels.js`:
```javascript
{
    num: 11,
    name: "UNKNOWN",
    desc: "Experimental, uncategorized, and anomalous broadcasts.",
    color: "#ff0000",
    programs: [
        {
            title: "YOUR PROGRAM TITLE",
            author: "your-handle",
            duration: 15,
            html: '<div style="color:#fff">Your HTML content here</div>'
        }
        // ... add before the closing ]
    ]
}
```

## Aesthetic

- **CRT TV frame**: Vintage wood-grain border with scanlines
- **Signal bars**: Digital signal strength indicator (████░░░░░)
- **Rebuffering**: Static effect between channel/program changes
- **Color palette**: Purple (#8b008b), magenta (#ff69b4), green (#0f0), red (#ff0000)
- **Font**: MS Gothic monospace (retro terminal aesthetic)

## NHI Pet Integration

Channel 03 (ART) and Channel 11 (UNKNOWN) feature the NHI digital pet — a low-poly, alien entity that:
- Floats and rotates with bio-luminescent pulse
- Follows mouse cursor with three eye-sensors
- Cycles through 6 moods on click (idle → curious → happy → excited → sleepy)
- Gets "hungry" if left alone too long
- Has tentacle limbs, spires, rune sigils, and drifting ash particles

## Deployment

### Neocities (existing site)
Upload all files to your Neocities site root:
```
public_access_tv.html       → index.html (rename so it's your homepage)
public_access_channels.js   → /
public_access_submit.html   → /submit.html
nhi_pet.js                  → /
nhi_pet_widget.html         → /widget.html
nhi_pet_demo.html           → /demo.html
```

The TV page loads Three.js from CDN (same as your existing `nolove.neocities.org`) and works standalone — no Neocities-specific APIs are required.

### Docker (if you have docker-compose)
```bash
echo "FROM nginx:alpine
COPY . /usr/share/nginx/html" > Dockerfile

docker build -t public-access-channel .
docker run -p 8080:80 public-access-channel
# Visit: http://localhost:8080/public_access_tv.html
```

### Updating from GitHub
If you've forked/cloned and want to pull latest changes:
```bash
git pull origin main
```

Then re-upload to Neocities or redeploy to GitHub Pages.

## Contributing

1. **Fork** this repository
2. **Add your program** to `public_access_channels.js` (any channel)
3. **Test locally**: open `public_access_tv.html` in a browser
4. **Push** your changes
5. **Submit a PR** — or open an issue with your program and I'll add it

See `public_access_submit.html` for a form that generates the program JSON automatically.
