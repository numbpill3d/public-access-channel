# Public Access Channel — Tiny Website Broadcasting Network

A tiny website broadcasting network where people publish short pieces of HTML to numbered channels. The homepage TV rotates through channels every few minutes, and visitors can tune manually.

Think public-access television, except each program is somebody's webpage.

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

Upload all files to your Neocities site root:
```
public_access_tv.html       → index.html (or keep as is)
public_access_channels.js   → /
public_access_submit.html   → / (or link from your site)
nhi_pet.js                  → /
```

The TV page loads Three.js from CDN (same as your existing site) and works standalone.
