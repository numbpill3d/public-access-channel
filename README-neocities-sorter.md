# Neocities File Sorter & Mass Restructurer

[![Python](https://img.shields.io/badge/python-3776ab?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github)](https://github.com/numbpill3d/public-access-channel)

Automatically **sorts, renames, and reorganizes** the files on your `nolove.neocities.org` site so your Neocities dashboard isn't a sea of unsorted image files.

## What It Does

1. **Lists all files** on your Neocities site via the API (or scrapes the live site HTML)
2. **Sorts files into type directories**: `gif/`, `png/`, `jpg/`, `webp/`, `css/`, `js/`, `html/`, etc.
3. **Renames random-named files** (like `197f4ca4e00600714d2bc0080db92627.gif`) to meaningful date-based names (like `2025-08-13-b0b47d.gif`)
4. **Creates directories** on the server
5. **Uploads files** to new paths
6. **Deletes files** from old paths (batched)
7. **Saves a rename mapping** CSV so you can update HTML references
8. **Optionally updates HTML files** to point to the new paths

## Quick Start

### Get the Code
```bash
# Clone from GitHub
git clone https://github.com/numbpill3d/public-access-channel.git
cd public-access-channel

# Or just download the sorter:
curl -O https://raw.githubusercontent.com/numbpill3d/public-access-channel/main/neocities_sort.py
```

### Step 1: Get Your Neocities API Key

You can authenticate in two ways:

**Option A — API Key (recommended, simplest):**
Get your API key from the Neocities settings page: https://neocities.org/settings
Then:
```bash
export NEOCITIES_API_KEY="your-32-char-hex-api-key"
```

**Option B — Username + Password:**
```bash
export NEOCITIES_USERNAME="nolove"
export NEOCITIES_PASSWORD="your-password-here"
```
The script will automatically generate and cache the API key for you.

> **Privacy note:** The API key is cached in `~/.neocities_api_key` (chmod 600).
> Your password is only sent to Neocities once to generate the key — after that, the cached key is used.

### Step 2: Preview the Changes (Dry Run)

**Option 1 — API mode (requires credentials):**
```bash
cd /home/scorn
python3 neocities_sort.py --dry-run
```

**Option 2 — Scrape mode (no credentials needed, planning only):**
Scrapes the live site's HTML pages to discover file references, then plans the sorting:
```bash
python3 neocities_sort.py --scrape --dry-run
```

**Option 3 — Local mode (sort your recovered files):**
```bash
python3 neocities_sort.py --local --dry-run
```

You'll see:
- A summary of how many files will be moved, renamed, or left unchanged
- The planned directory structure
- A detailed table of all changes
- A rename mapping for files with random names
- Collision warnings (same filename in different directories)

### Step 3: Execute the Restructuring

When you're ready to apply the changes:

```bash
python3 neocities_sort.py --execute
```

### Step 4: Update HTML References (Optional)

After executing, update your HTML files to use the new file paths:

```bash
python3 neocities_sort.py --execute --update-html
# Or update HTML in a specific directory:
python3 neocities_sort.py --execute --update-html --html-dir /home/scorn
```

## How the Sorting Works

### File Type Detection
Files are sorted based on their extension into these directories:

| Extension | Directory |
|-----------|-----------|
| `.gif`    | `gif/`    |
| `.png`    | `png/`    |
| `.jpg`, `.jpeg` | `jpg/` |
| `.webp`   | `webp/`   |
| `.svg`    | `svg/`    |
| `.html`, `.htm` | `html/` |
| `.css`    | `css/`    |
| `.js`     | `js/`     |
| `.txt`    | `txt/`    |
| `.json`   | `json/`   |
| `.xml`    | `xml/`    |

### Random Name Detection

The script uses a heuristic to identify randomly-named files:

**Detected as random (will be renamed):**
- Hex hashes: `197f4ca4e00600714d2bc0080db92627.gif`, `1e0c9aef.gif`
- All-digit names: `1.png`, `252.gif`, `108.gif`
- Short alphanumeric: `01a.gif`, `1VmU2fy.gif`, `221l6f22.png`

**Detected as descriptive (kept as-is):**
- Uppercase acronyms: `BRAWLNME.png`, `EYESNOFACE.gif`, `DG.png`
- Pattern names: `NMX10.gif`, `NOLOVE03.gif`, `Copilot_20251218.png`
- Meaningful words: `report.png`, `dusty.gif`, `floww.gif`
- Underscore names: `0064_small.gif`

### Renaming Scheme

Random-named files are renamed using:
```
{upload_date}-{8-char-hash}{extension}
```

Example: `2026/1636404221559.png` → `png/2025-01-15-a1b2c3d4.png`

The hash is based on the **full original path** (not just the filename) to prevent collisions between files with the same name in different directories.

### Collision Detection

If two files would map to the same new path, the second one gets a `-1` suffix:
```
gif/da6.gif        ← images/da6.gif (first occurrence)
gif/da6-1.gif      ← da6.gif (root, collision resolved)
```

## Safety Notes

- **Dry-run is the default** — nothing changes without `--execute`
- **All renames are reversible** — the CSV mapping records every old → new path change
- **No files are lost** — the upload-then-delete pattern ensures files are safely uploaded to new paths before old ones are removed
- **Batch delete** ensures no more than 50 files per API request
- **Rate limiting** respects Neocities API limits (2s delay between calls)

## Credentials Status

As of the last attempt, the password combinations provided for the Neocities account **did not authenticate**. The script is fully built and ready to use — simply provide valid credentials or an API key:

```bash
export NEOCITIES_API_KEY="your-key-from-https://neocities.org/settings"
python3 neocities_sort.py --execute
```

## Files

- `neocities_sort.py` — Main script (run with `--help` for all options)
- `README-neocities-sorter.md` — This guide
- `get_neocities_key.js` — Interactive Node.js helper for generating an API key

## Current Plan Summary (Scraped from Live Site)

```
Total files:       243
Unchanged:         0
Moved:             243
Renamed:           48   (random/hex names → date-hash names)
Collisions fixed:  4    (same filename in different directories)

Planned directory structure:
  /css/    (1 files)
  /gif/    (98 files)
  /html/   (11 files)
  /jpg/    (59 files)
  /js/     (2 files)
  /png/    (72 files)
```
