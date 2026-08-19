#!/usr/bin/env python3
"""
Neocities File Sorter & Mass Restructurer
==========================================

Sorts and restructures file paths on your Neocities site (nolove.neocities.org).

Usage:
    # Option A: Export your Neocities credentials as environment variables:
    export NEOCITIES_USERNAME="your-neocities-username"
    export NEOCITIES_PASSWORD="your-neocities-password"

    # Option B: Or directly provide an API key (get one at https://neocities.org/settings):
    export NEOCITIES_API_KEY="your-32-char-hex-api-key"

    # 2. Preview what the script WOULD do (dry run — no changes made):
    python3 neocities_sort.py --dry-run

    # 3. Actually execute the restructuring:
    python3 neocities_sort.py --execute

    # 4. Only sort (no renaming of random files):
    python3 neocities_sort.py --dry-run --sort-only

    # 5. Sort and rename, then auto-update HTML references:
    python3 neocities_sort.py --execute --update-html

    # 6. Scrape the live site HTML for file references (no API auth needed, planning only):
    python3 neocities_sort.py --scrape --dry-run

Features:
    - Fetches your current file listing from the Neocities API (or scrapes site HTML)
    - Generates an API key (first time) or accepts a pre-generated key via env var
    - Sorts all files into type-based directories: gif/, png/, jpg/, webp/, html/, css/, js/
    - Renames files with random/hex names to meaningful date-based names
    - Creates directories on the server via API
    - Uploads files to new paths
    - Deletes files from old paths
    - Generates a rename mapping CSV for updating HTML references
    - Supports dry-run mode to preview all changes before committing

API Reference: https://neocities.org/api
"""

import os
import sys
import json
import csv
import time
import hashlib
import argparse
import requests
from pathlib import Path
from datetime import datetime

# ─── Configuration ───────────────────────────────────────────────────────────

SITE_NAME = "nolove"  # nolove.neocities.org
API_BASE = "https://neocities.org/api"
API_KEY_FILE = Path.home() / ".neocities_api_key"
RENAME_MAP_FILE = Path.home() / ".neocities_rename_map.csv"
RATE_LIMIT_DELAY = 2  # seconds between API calls (Neocities recommends ~1/min for recurring updates,
                       # but we batch operations to be efficient while respecting limits)

# Extensions to sort into directories by type
TYPE_DIRS = {
    ".gif": "gif",
    ".png": "png",
    ".jpg": "jpg",
    ".jpeg": "jpg",
    ".webp": "webp",
    ".svg": "svg",
    ".html": "html",
    ".htm": "html",
    ".css": "css",
    ".js": "js",
    ".txt": "txt",
    ".json": "json",
    ".xml": "xml",
}


# ─── Neocities API Client ────────────────────────────────────────────────────

class NeocitiesAPI:
    def __init__(self, username=None, password=None, api_key=None):
        self.username = username
        self.password = password
        self.api_key = api_key

    def _basic_auth(self):
        """Basic auth header for username/password requests."""
        import base64
        credentials = f"{self.username}:{self.password}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return {"Authorization": f"Basic {encoded}"}

    def _api_key_auth(self):
        """API key auth header for all requests after key generation."""
        return {"Authorization": f"Bearer {self.api_key}"}

    def get_api_key(self):
        """
        Fetch an API key from Neocities using username/password.
        If an API key was already provided (via constructor), validate and use it.
        Caches the key in ~/.neocities_api_key for reuse.
        """
        # If API key was provided directly, validate it
        if self.api_key:
            resp = requests.get(
                f"{API_BASE}/info",
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            if resp.status_code == 200 and resp.json().get("result") == "success":
                print(f"✅ API key validated successfully")
                return self.api_key
            else:
                print(f"❌ Provided API key is invalid: {resp.json()}")
                sys.exit(1)

        # Try to load cached key first
        if API_KEY_FILE.exists():
            cached_key = API_KEY_FILE.read_text().strip()
            # Validate it works
            resp = requests.get(
                f"{API_BASE}/info",
                headers={"Authorization": f"Bearer {cached_key}"}
            )
            if resp.status_code == 200 and resp.json().get("result") == "success":
                self.api_key = cached_key
                print(f"✅ Loaded cached API key from {API_KEY_FILE}")
                return self.api_key

        # Generate a new key
        resp = requests.get(f"{API_BASE}/key", headers=self._basic_auth())
        if resp.status_code == 200:
            data = resp.json()
            if data.get("result") == "success":
                self.api_key = data["api_key"]
                API_KEY_FILE.write_text(self.api_key)
                try:
                    API_KEY_FILE.chmod(0o600)
                except OSError:
                    pass  # Windows doesn't support chmod the same way
                print(f"✅ Generated and cached new API key at {API_KEY_FILE}")
                return self.api_key
            else:
                print(f"❌ API key generation failed: {data}")
                sys.exit(1)
        else:
            print(f"❌ Failed to get API key (HTTP {resp.status_code}): {resp.text}")
            sys.exit(1)

    def list_files(self, path=None):
        """
        List all files on the site. If path is None, lists everything recursively
        by paginating through directories.
        Returns a list of file dicts with keys: path, is_directory, size, updated_at, sha1_hash.
        """
        all_files = []
        to_process = ["."] if path is None else [path]

        while to_process:
            current_path = to_process.pop(0)
            url = f"{API_BASE}/list"
            if current_path != ".":
                url += f"?path={current_path}"

            resp = requests.get(url, headers={"Authorization": f"Bearer {self.api_key}"})
            if resp.status_code != 200:
                print(f"⚠️  Failed to list path '{current_path}': {resp.status_code} {resp.text}")
                continue

            data = resp.json()
            if data.get("result") != "success":
                print(f"⚠️  API error listing '{current_path}': {data}")
                continue

            for entry in data.get("files", []):
                if entry["is_directory"]:
                    # Queue subdirectories for recursive listing
                    full_path = entry["path"]
                    to_process.append(full_path)
                else:
                    all_files.append(entry)

            time.sleep(RATE_LIMIT_DELAY)

        return all_files

    def create_directory(self, path):
        """Create a directory on the server."""
        resp = requests.post(
            f"{API_BASE}/create_directory",
            headers={"Authorization": f"Bearer {self.api_key}"},
            data={"path": path}
        )
        return resp.json()

    def upload_file(self, local_path, remote_path):
        """
        Upload a single file to the server.
        local_path: path to the local file
        remote_path: destination path on Neocities
        """
        # The filename in the multipart form field name IS the remote path
        with open(local_path, "rb") as f:
            files = {remote_path: f}
            resp = requests.post(
                f"{API_BASE}/upload",
                headers={"Authorization": f"Bearer {self.api_key}"},
                files=files
            )
        return resp.json()

    def delete_files(self, paths):
        """
        Delete multiple files from the server in one request.
        paths: list of file paths to delete
        """
        data = {"filenames[]": paths}
        resp = requests.post(
            f"{API_BASE}/delete",
            headers={"Authorization": f"Bearer {self.api_key}"},
            data=data
        )
        return resp.json()

    def download_file(self, remote_path, local_path):
        """Download a file from the Neocities site to local disk."""
        resp = requests.get(
            f"https://{SITE_NAME}.neocities.org/{remote_path}",
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        if resp.status_code == 200:
            Path(local_path).parent.mkdir(parents=True, exist_ok=True)
            with open(local_path, "wb") as f:
                f.write(resp.content)
            return True
        return False

    def get_site_info(self):
        """Get basic site info."""
        resp = requests.get(
            f"{API_BASE}/info",
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        return resp.json()

    def list_files_public(self):
        """
        Scrape the live site for file references without requiring API auth.
        Fetches all HTML pages and extracts local file references.
        Limited to files actually referenced in HTML (not full listing).
        """
        site_base = f"https://{SITE_NAME}.neocities.org"
        ext_map = {k.lstrip('.'): v for k, v in TYPE_DIRS.items()}
        
        # Known HTML pages to scrape
        pages_to_check = [
            "/", "/index.html", "/gallery", "/gallery.html", "/monument",
            "/monument.html", "/about", "/about.html", "/diary", "/diary.html",
            "/links", "/links.html",
        ]

        all_refs = set()
        html_files_found = set()

        for page in pages_to_check:
            url = f"{site_base}{page}"
            resp = requests.get(url, timeout=10)
            if resp.status_code != 200:
                continue
            if page.strip("/") in ("", "index") or ".html" not in page:
                html_files_found.add("index.html") if page == "/" else html_files_found.add(page.strip("/").split('/')[-1] if page else "index.html")
            
            # Extract all src and href references
            import re as re_mod
            refs = re_mod.findall(r'(?:src|href)="([^"]+)"', resp.text)
            for ref in refs:
                if ref.startswith(('http', '//', '#', 'data:', 'mailto:', 'tel:')):
                    continue
                if ref.startswith('/'):
                    ref = ref.lstrip('/')
                if not ref.strip():
                    continue
                ext = os.path.splitext(ref)[1].lower().lstrip('.')
                if ext in ext_map or ext in ('html', 'htm', 'css', 'js'):
                    all_refs.add(ref)

        # Convert to file list format
        files = []
        for ref in sorted(all_refs):
            ext = os.path.splitext(ref)[1].lower().lstrip('.')
            ftype = ext_map.get(ext, ext)
            # Try to get file size via HEAD request
            size = 0
            try:
                head_resp = requests.head(f"{site_base}/{ref}", timeout=5)
                if head_resp.status_code == 200:
                    size = int(head_resp.headers.get('content-length', 0))
            except Exception:
                pass
            files.append({'path': ref, 'type': ftype, 'size': size, 'updated_at': ''})

        return files


# ─── Sorting Logic ────────────────────────────────────────────────────────────

def is_descriptive_name(filename):
    """
    Heuristic: returns True if a filename looks like a real, meaningful name
    (not a random hex string or numeric hash).

    Examples of 'random' (→ will be renamed):
        - 197f4ca4e00600714d2bc0080db92627.gif  (hex hash)
        - 1e0c9aef.gif                         (short hex string)
        - 01a.gif                              (short random alphanumeric)
        - 1VmU2fy.gif                          (short random alphanumeric)
        - 221l6f22.png                         (random mix)
        - 1636404221559.png                    (all digits, long)
        - 108.gif, 108.gif, etc.               (all digits)

    Examples of 'descriptive' (→ kept as-is):
        - BRAWLNME.png                         (all uppercase words)
        - EYESNOFACE.gif                       (all uppercase words)
        - DG.png / DG2.png                     (all uppercase words)
        - HAPPIESTTIMEOF MY LIFE.png           (contains spaces)
        - Copilot_20251218_083111.png          (known pattern)
        - Gemini_Generated_Image_xycqysxycq.png (known pattern)
        - NMX10.gif                            (consistent pattern: letters+digits)
        - 0064_small.gif                       (has meaningful underscore word)
        - report.png                           (lowercase word)
    """
    name = Path(filename).stem  # filename without extension

    # Known descriptive patterns (AI-generated, Copilot, etc.)
    if any(pattern in name for pattern in ["Copilot", "Gemini", "Generated"]):
        return True

    # If it's all digits, it's auto-generated
    if name.isdigit():
        return False

    # If all uppercase letters (like BRAWLNME, EYESNOFACE, DG2), it's descriptive
    if name.isupper() and any(c.isalpha() for c in name):
        return True

    # Very short names (2 chars or less) that aren't all uppercase are likely auto-generated
    if len(name) <= 2:
        return False

    # If it contains spaces, underscores, or hyphens forming multi-word names
    clean = name.replace("_", " ").replace("-", " ")
    words = [w for w in clean.split() if w]
    if len(words) >= 2:
        return True

    # If it's a mix of letters and digits with a recognizable pattern
    # e.g., NMX10, NM2 — has a letter prefix (>=2 chars) followed by digits
    letter_prefix = ""
    digit_suffix = ""
    for c in name:
        if c.isalpha() and not digit_suffix:
            letter_prefix += c
        elif c.isdigit():
            digit_suffix += c
        else:
            break
    if len(letter_prefix) >= 2 and len(digit_suffix) >= 1 and len(name) == len(letter_prefix) + len(digit_suffix):
        return True

    # If it's all letters (a single word), it's descriptive
    # e.g., "report", "logo", "photo"
    if name.isalpha():
        return True

    # Hex strings (any length >= 4 that's all hex chars) are likely random hashes
    # e.g., "1e0c9aef", "0223f3fcf..."
    if len(name) >= 4 and all(c in "0123456789abcdefABCDEF" for c in name):
        return False

    # Short alphanumeric (3-8 chars) without clear word structure — likely random
    # e.g., "01a", "1VmU2fy", "221l6f22"
    return False


def generate_meaningful_name(old_filename, upload_date, old_path=""):
    """
    Generate a meaningful filename for a file with a random name.
    Uses the upload date, a short hash of the original name (including path for uniqueness),
    and the original extension.

    Args:
        old_filename: The original filename (e.g., "01a.gif")
        upload_date: RFC2822 date string from the API
        old_path: The full original path (e.g., "2026/1.png") for collision avoidance
    """
    stem = Path(old_filename).stem
    ext = Path(old_filename).suffix.lower()
    # Use the full old path (not just stem) so files in different dirs don't collide
    hash_source = old_path if old_path else old_filename
    short_hash = hashlib.md5(hash_source.encode()).hexdigest()[:8]

    # Parse upload date
    try:
        dt = datetime.strptime(upload_date, "%a, %d %b %Y %H:%M:%S %z")
        date_str = dt.strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        date_str = "unknown-date"

    new_name = f"{date_str}-{short_hash}{ext}"
    return new_name


def plan_sorting(files, rename=True):
    """
    Plan the sorted structure for all files.

    Returns a list of dicts:
    {
        "old_path": str,          # current path on the server
        "new_path": str,          # planned new path
        "type": str,              # 'moved', 'renamed', 'moved+renamed', 'unchanged'
        "size": int,
        "old_name": str,
        "new_name": str,
        "upload_date": str,
    }
    """
    plan = []

    for f in files:
        old_path = f["path"]
        filename = Path(old_path).name
        size = f.get("size", 0)
        upload_date = f.get("updated_at", "")

        ext = Path(filename).suffix.lower()
        type_dir = TYPE_DIRS.get(ext, "other")
        is_descriptive = is_descriptive_name(filename)

        if not is_descriptive and rename:
            new_name = generate_meaningful_name(filename, upload_date, old_path)
        else:
            new_name = filename

        new_path = f"{type_dir}/{new_name}" if type_dir != "other" else new_name

        # Determine the type of change
        old_dir = str(Path(old_path).parent)
        if old_dir == ".":
            old_dir = ""
        new_dir = type_dir if type_dir != "other" else ""

        if old_path == new_path:
            change_type = "unchanged"
        elif new_name == filename and old_dir != new_dir:
            change_type = "moved"
        elif new_name != filename and old_dir != new_dir:
            change_type = "moved+renamed"
        elif new_name != filename and old_dir == new_dir:
            change_type = "renamed"
        else:
            change_type = "moved"

        plan.append({
            "old_path": old_path,
            "new_path": new_path,
            "type": change_type,
            "size": size,
            "old_name": filename,
            "new_name": new_name,
            "upload_date": upload_date,
            "old_dir": old_dir,
            "new_dir": new_dir,
        })

    # Collision detection: ensure no two files map to the same new_path
    seen_paths = {}
    for p in plan:
        np = p["new_path"]
        if np in seen_paths:
            # Append a counter to make it unique
            counter = 1
            stem = Path(np).stem
            ext = Path(np).suffix
            type_dir = p["new_dir"]
            while f"{type_dir}/{stem}-{counter}{ext}" in seen_paths or f"{stem}-{counter}{ext}" in [pp["new_path"] for pp in plan]:
                counter += 1
            old_np = p["new_path"]
            if type_dir:
                p["new_path"] = f"{type_dir}/{stem}-{counter}{ext}"
            else:
                p["new_path"] = f"{stem}-{counter}{ext}"
            p["new_name"] = Path(p["new_path"]).name
            # Update change type
            if p["old_name"] != p["new_name"] and p["old_dir"] != p["new_dir"]:
                p["type"] = "moved+renamed"
            elif p["old_name"] != p["new_name"]:
                p["type"] = "renamed"
            print(f"  ⚠️  Collision detected: {old_np} → {p['new_path']} (adjusted)")
        else:
            seen_paths[np] = p

    return plan


def print_plan(plan, dry_run=True):
    """Print a summary of the sorting plan."""
    total = len(plan)
    unchanged = sum(1 for p in plan if p["type"] == "unchanged")
    moved = sum(1 for p in plan if p["type"] in ("moved", "moved+renamed"))
    renamed = sum(1 for p in plan if p["type"] in ("renamed", "moved+renamed"))

    mode = "DRY RUN — " if dry_run else "EXECUTE — "
    print(f"\n{'='*70}")
    print(f"{mode}Neocities File Sort Plan for {SITE_NAME}.neocities.org")
    print(f"{'='*70}")
    print(f"Total files:       {total}")
    print(f"Unchanged:         {unchanged}")
    print(f"Moved:             {moved}")
    print(f"Renamed:           {renamed}")
    print(f"Total size:        {sum(p['size'] for p in plan) / 1024 / 1024:.1f} MB")
    print(f"{'='*70}\n")

    # Show directory structure plan
    print("Planned directory structure:")
    dirs = set()
    for p in plan:
        dirs.add(p["new_dir"] if p["new_dir"] else "(root)")
    for d in sorted(dirs):
        count = sum(1 for p in plan if (p["new_dir"] if p["new_dir"] else "(root)") == d)
        print(f"  /{d}/  ({count} files)")
    print()

    # Show changes
    changed = [p for p in plan if p["type"] != "unchanged"]
    if not changed:
        print("No changes needed — all files are already sorted!")
        return

    print("Changes:")
    print(f"{'Type':<16} {'Size':>10}  {'Old Path':<55} {'New Path'}")
    print("-" * 120)
    for p in changed:
        size_str = f"{p['size']/1024:.0f}KB" if p["size"] > 1024 else f"{p['size']}B"
        old_path = p["old_path"]
        new_path = p["new_path"]
        if len(old_path) > 53:
            old_path = old_path[:50] + "..."
        print(f"{p['type']:<16} {size_str:>10}  {old_path:<55} {new_path}")
    print()


def print_rename_map(plan):
    """Print files that will be renamed."""
    renamed = [p for p in plan if p["type"] in ("renamed", "moved+renamed") and p["old_name"] != p["new_name"]]
    if not renamed:
        print("\nNo files need renaming — all have descriptive names.")
        return

    print(f"\n{'='*70}")
    print(f"Rename mapping ({len(renamed)} files):")
    print(f"{'='*70}")
    print(f"{'Old Name':<45} {'→':^3} {'New Name'}")
    print("-" * 90)
    for p in renamed:
        old_name = p["old_name"]
        new_name = p["new_name"]
        if len(old_name) > 43:
            old_name = old_name[:40] + "..."
        print(f"{old_name:<45} {'→':^3} {new_name}")
    print()


def save_rename_map(plan):
    """Save a CSV mapping of old paths to new paths for updating HTML references."""
    renamed = [p for p in plan if p["type"] != "unchanged"]
    if not renamed:
        return

    with open(RENAME_MAP_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["old_path", "new_path", "old_filename", "new_filename", "change_type"])
        for p in renamed:
            writer.writerow([p["old_path"], p["new_path"], p["old_name"], p["new_name"], p["type"]])

    print(f"✅ Rename mapping saved to {RENAME_MAP_FILE}")


def update_html_references(html_dir, rename_map_path):
    """Update HTML files to use new file paths instead of old ones.
    
    Handles both:
    - Full path references: src="2026/1.png" → src="png/date-hash.png"
    - Filename-only references: src="1.png" → src="png/date-hash.png"
    - Relative references within subdirectories
    
    Uses regex-based replacement to avoid double-replacing filenames
    that are already part of updated paths (e.g., won't turn "gif/5A.gif"
    into "gif/gif/5A.gif" when updating standalone "5A.gif" references).
    """
    import re as re_mod

    if not Path(rename_map_path).exists():
        print(f"⚠️  No rename map found at {rename_map_path}")
        return

    # Load the rename mapping
    full_map = {}      # "2026/1.png" → "png/date-hash.png"
    filename_map = {}  # "1.png" → "png/date-hash.png"
    with open(rename_map_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            old_path = row["old_path"]
            new_path = row["new_path"]
            old_filename = row["old_filename"]

            if old_path != new_path:
                full_map[old_path] = new_path
                full_map["./" + old_path] = "./" + new_path

                if old_filename not in filename_map:
                    filename_map[old_filename] = new_path

    if not full_map:
        print("No mappings to apply.")
        return

    # Sort by length (longest first) to avoid partial matches
    sorted_full = sorted(full_map.items(), key=lambda x: len(x[0]), reverse=True)
    sorted_filename = sorted(filename_map.items(), key=lambda x: len(x[0]), reverse=True)

    html_files = list(Path(html_dir).rglob("*.html"))
    html_files += list(Path(html_dir).rglob("*.htm"))

    if not html_files:
        print(f"No HTML files found in {html_dir}")
        return

    updated_count = 0
    total_replacements = 0

    for html_file in html_files:
        content = html_file.read_text(encoding="utf-8", errors="replace")
        original_content = content
        file_replacements = 0

        # Step 1: Replace full path references
        # Match complete quoted path values to avoid substring issues
        # e.g., "2026/1.png" → "png/new.png"
        # Also handle single-quoted, unquoted (in url()), and JS array contexts
        for old_ref, new_ref in sorted_full:
            # Double-quoted: "old_path" → "new_path"
            old_q = f'"{old_ref}"'
            new_q = f'"{new_ref}"'
            count = content.count(old_q)
            if count:
                content = content.replace(old_q, new_q)
                file_replacements += count

            # Single-quoted: 'old_path' → 'new_path'
            old_sq = f"'{old_ref}'"
            new_sq = f"'{new_ref}'"
            count = content.count(old_sq)
            if count:
                content = content.replace(old_sq, new_sq)
                file_replacements += count

            # In url(): url(old_path) → url(new_path)
            old_url = f"url({old_ref})"
            new_url = f"url({new_ref})"
            count = content.count(old_url)
            if count:
                content = content.replace(old_url, new_url)
                file_replacements += count

        # Step 2: Replace standalone filename references
        # Only match when filename is a complete quoted value (not inside a longer path)
        # e.g., "1.png" → "png/new.png" but NOT inside "png/1.png"
        for old_name, new_path in sorted_filename:
            # Double-quoted standalone filename
            old_fn_q = f'"{old_name}"'
            new_fn_q = f'"{new_path}"'
            count = content.count(old_fn_q)
            if count:
                content = content.replace(old_fn_q, new_fn_q)
                file_replacements += count

            # Single-quoted standalone filename
            old_fn_sq = f"'{old_name}'"
            new_fn_sq = f"'{new_path}'"
            count = content.count(old_fn_sq)
            if count:
                content = content.replace(old_fn_sq, new_fn_sq)
                file_replacements += count

            # url() standalone filename
            old_fn_url = f"url({old_name})"
            new_fn_url = f"url({new_path})"
            count = content.count(old_fn_url)
            if count:
                content = content.replace(old_fn_url, new_fn_url)
                file_replacements += count

        if content != original_content:
            html_file.write_text(content, encoding="utf-8")
            updated_count += 1
            print(f"  Updated: {html_file.name} ({file_replacements} replacements)")
            total_replacements += file_replacements

    print(f"✅ Updated {updated_count} HTML files ({total_replacements} total path replacements)")


# ─── Execution ───────────────────────────────────────────────────────────────

def execute_plan(api, plan, download_dir=None):
    """
    Execute the sorting plan on the server:
    1. Create necessary directories
    2. Download files that need moving/renaming (from server)
    3. Upload to new paths
    4. Delete old paths
    5. Save rename mapping

    If download_dir is provided, downloads files there temporarily.
    Otherwise, downloads to a temp directory and cleans up.
    """
    changed = [p for p in plan if p["type"] != "unchanged"]
    if not changed:
        print("Nothing to execute — all files already sorted.")
        return

    # Step 1: Create directories
    dirs_to_create = set()
    for p in changed:
        if p["new_dir"]:
            dirs_to_create.add(p["new_dir"])

    print(f"\n📁 Creating {len(dirs_to_create)} directories...")
    for d in sorted(dirs_to_create):
        resp = api.create_directory(d)
        print(f"  → {d}: {resp.get('result', 'unknown')}")
        time.sleep(RATE_LIMIT_DELAY)

    # Step 2: Download files that need moving/renaming
    import tempfile
    temp_dir = Path(download_dir) if download_dir else Path(tempfile.mkdtemp(prefix="neocities_"))
    temp_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n⬇️  Downloading {len(changed)} files from server...")
    download_ok = 0
    for i, p in enumerate(changed):
        local_path = temp_dir / p["old_path"].replace("/", "_")
        ok = api.download_file(p["old_path"], str(local_path))
        if ok:
            download_ok += 1
        else:
            print(f"  ⚠️  Failed to download {p['old_path']}")
        if (i + 1) % 10 == 0:
            print(f"  ...{i+1}/{len(changed)} downloaded")
        time.sleep(RATE_LIMIT_DELAY)

    print(f"  Downloaded {download_ok}/{len(changed)} files")

    # Step 3: Upload to new paths
    print(f"\n⬆️  Uploading {len(changed)} files to new paths...")
    upload_ok = 0
    for i, p in enumerate(changed):
        local_path = temp_dir / p["old_path"].replace("/", "_")
        if not local_path.exists():
            print(f"  ⚠️  Local file missing for {p['old_path']}")
            continue
        resp = api.upload_file(str(local_path), p["new_path"])
        if resp.get("result") == "success":
            upload_ok += 1
        else:
            print(f"  ⚠️  Failed to upload {p['old_path']} → {p['new_path']}: {resp}")
        if (i + 1) % 10 == 0:
            print(f"  ...{i+1}/{len(changed)} uploaded")
        time.sleep(RATE_LIMIT_DELAY)

    print(f"  Uploaded {upload_ok}/{len(changed)} files")

    # Step 4: Delete old files (batch)
    print(f"\n🗑️  Deleting {len(changed)} old files...")
    # Batch delete in groups of 10 (API limit is 50 per request)
    batch_size = 10
    deleted_ok = 0
    for i in range(0, len(changed), batch_size):
        batch = [p["old_path"] for p in changed[i:i+batch_size]]
        resp = api.delete_files(batch)
        if resp.get("result") == "success":
            deleted_ok += len(batch)
            print(f"  → Deleted batch {i//batch_size + 1}: {len(batch)} files")
        else:
            print(f"  ⚠️  Failed to delete batch: {resp}")
        time.sleep(RATE_LIMIT_DELAY)

    print(f"  Deleted {deleted_ok}/{len(changed)} files")

    # Step 5: Save rename map
    save_rename_map(plan)

    # Cleanup temp dir
    if not download_dir:
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
        print(f"\n  Cleaned up temporary directory")

    print(f"\n✅ Done! {upload_ok} files uploaded, {deleted_ok} files deleted.")


# ─── Local Mode ───────────────────────────────────────────────────────────────

def sort_local_files(local_dir, dry_run=True, rename=True):
    """
    Sort files in a local directory by type.
    Moves files into subdirectories based on their extension.
    Uses the same plan_sorting() logic as the API mode for consistency,
    including collision detection and random-name renaming.
    """
    local_dir = Path(local_dir)
    if not local_dir.exists():
        print(f"❌ Directory not found: {local_dir}")
        return

    print(f"\n📂 Sorting local files in: {local_dir}")

    # Build plan for local files (flatten all subdirectories)
    all_files = [f for f in local_dir.rglob("*") if f.is_file() and not f.is_symlink()]
    print(f"   Found {len(all_files)} files (flattening nested directories)")

    # Convert to the format expected by plan_sorting()
    file_list = []
    for f in all_files:
        rel_path = str(f.relative_to(local_dir))
        ext = f.suffix.lower()
        ftype = TYPE_DIRS.get(ext, "other")
        file_list.append({
            'path': rel_path,
            'type': ftype,
            'size': f.stat().st_size,
            'updated_at': f.stat().st_mtime,  # file modification time as date
        })

    # Use the same plan_sorting() function for consistency
    plan = plan_sorting(file_list, rename=rename)

    # Convert plan to local actions
    from collections import Counter
    dirs_needed = set()
    moves = []
    for item in plan:
        if item['type'] != 'unchanged':
            old_path = local_dir / item['old_path']
            new_path = local_dir / item['new_path']
            dirs_needed.add(item['new_dir']) if item['new_dir'] else None
            moves.append((item['old_path'], item['new_path'], old_path, new_path))

    # Show what we'd do
    print(f"\n   Actions: {len(moves)} files to move/rename")
    dir_dist = Counter()
    for old_rel, new_rel, old_abs, new_abs in moves:
        parts = new_rel.split('/')
        dir_name = parts[0] if len(parts) > 1 else '(root)'
        dir_dist[dir_name] += 1
    for d, count in sorted(dir_dist.items()):
        print(f"  /{d}/  ({count} files)")

    if dry_run:
        print(f"\n  Changes:")
        print(f"  {'Type':<16} {'Size':>10}  {'Old Path':<50} {'New Path'}")
        print("  " + "-" * 110)
        for item in plan:
            if item['type'] != 'unchanged':
                size_str = f"{item['size']/1024:.0f}KB" if item['size'] > 1024 else f"{item['size']}B"
                old = item['old_path']
                new = item['new_path']
                if len(old) > 48: old = old[:45] + "..."
                print(f"  {item['type']:<16} {size_str:>10}  {old:<50} {new}")
        print(f"\n  (Dry run — no changes made. Run with --local --execute to apply)")
        return

    # Execute: create dirs and move files
    for d in dirs_needed:
        if d:
            (local_dir / d).mkdir(exist_ok=True)

    moved = 0
    for item in plan:
        if item['type'] == 'unchanged':
            continue
        old_path = local_dir / item['old_path']
        new_path = local_dir / item['new_path']
        if not old_path.exists():
            print(f"  ⚠️  Source not found: {old_path}")
            continue
        new_path.parent.mkdir(parents=True, exist_ok=True)
        # Handle collisions (shouldn't happen due to plan_sorting, but just in case)
        if new_path.exists() and old_path != new_path:
            stem = new_path.stem
            ext = new_path.suffix
            counter = 1
            while new_path.exists():
                new_path = new_path.parent / f"{stem}-{counter}{ext}"
                counter += 1
        os.rename(str(old_path), str(new_path))
        moved += 1

    # Remove now-empty subdirectories
    for subdir in sorted(local_dir.rglob("*"), key=lambda x: len(str(x)), reverse=True):
        if subdir.is_dir() and subdir != local_dir:
            try:
                subdir.rmdir()  # only removes if empty
            except OSError:
                pass  # not empty, skip

    print(f"\n  ✅ Moved {moved} files into type directories")
    print(f"  🧹 Cleaned up empty subdirectories")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Sort and restructure files on your Neocities site",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--dry-run", action="store_true", default=True,
                        help="Preview changes without making them (default)")
    parser.add_argument("--execute", action="store_true",
                        help="Execute the changes (creates dirs, uploads, deletes)")
    parser.add_argument("--sort-only", action="store_true",
                        help="Only move files into type directories, don't rename random files")
    parser.add_argument("--local", action="store_true",
                        help="Sort files in a local directory instead of the live site")
    parser.add_argument("--local-dir", default=None,
                        help="Local directory to sort (use with --local)")
    parser.add_argument("--scrape", action="store_true",
                        help="Scrape the live site HTML for file references (no API auth needed, planning only)")
    parser.add_argument("--update-html", action="store_true",
                        help="After executing, update HTML files to use new paths")
    parser.add_argument("--html-dir", default=None,
                        help="Directory containing HTML files to update (default: home dir)")

    args = parser.parse_args()

    # If --execute is passed, override dry_run
    if args.execute:
        args.dry_run = False

    # ── Local mode ──
    if args.local:
        local_dir = args.local_dir or "/home/scorn/Documents/neocities-nolove-recovered"
        sort_local_files(local_dir, dry_run=args.dry_run)
        return

    # ── Scrape mode (no auth needed) ──
    if args.scrape:
        print(f"🕵️  Scraping live site {SITE_NAME}.neocities.org for file references...")
        api = NeocitiesAPI()  # No credentials needed for scraping
        files = api.list_files_public()
        print(f"   Found {len(files)} files (from HTML reference scraping)")
        
        rename = not args.sort_only
        plan = plan_sorting(files, rename=rename)
        print_plan(plan, dry_run=True)
        print_rename_map(plan)
        
        # Always save the mapping in scrape mode (it's planning only, no destructive actions)
        save_rename_map(plan)
        print(f"\n💡 Scrape mode is planning-only — no changes were made to your site.")
        print(f"\nTo execute the plan on the live site, you need valid API credentials:")
        print(f"  Get your API key from https://neocities.org/settings")
        print(f"  export NEOCITIES_API_KEY='your-32-char-api-key'")
        print(f"  python3 neocities_sort.py --execute")
        print(f"\nOr to update HTML files locally with the new paths:")
        print(f"  python3 neocities_sort.py --execute --update-html --html-dir /path/to/your/html")
        return

    # ── API mode ──
    api_key = os.environ.get("NEOCITIES_API_KEY")
    username = os.environ.get("NEOCITIES_USERNAME")
    password = os.environ.get("NEOCITIES_PASSWORD")

    if api_key:
        api = NeocitiesAPI(api_key=api_key)
    elif username and password:
        api = NeocitiesAPI(username=username, password=password)
    else:
        print("❌ Neocities credentials not found!")
        print("\nOption A — API key (recommended, get one at https://neocities.org/settings):")
        print("  export NEOCITIES_API_KEY='your-32-char-hex-api-key'")
        print("\nOption B — Username/password:")
        print("  export NEOCITIES_USERNAME='your-neocities-username'")
        print("  export NEOCITIES_PASSWORD='your-neocities-password'")
        print(f"\nYour site: https://{SITE_NAME}.neocities.org")
        sys.exit(1)

    print(f"🔌 Connecting to Neocities...")
    if api_key:
        print(f"   Using API key from NEOCITIES_API_KEY env var")
    else:
        print(f"   Using username: '{username}'")

    # Get or generate API key
    api.get_api_key()
    print(f"🔑 API key ready (cached at {API_KEY_FILE})")

    # Get site info
    info = api.get_site_info()
    print(f"   Site: {info.get('info', {}).get('sitename', 'unknown')}")
    print(f"   Hits: {info.get('info', {}).get('hits', '?')}")
    print(f"   Last updated: {info.get('info', {}).get('last_updated', '?')}")

    # List all files
    print(f"\n📋 Fetching file listing for {SITE_NAME}.neocities.org...")
    files = api.list_files()
    print(f"   Found {len(files)} files")

    # Plan the sorting
    rename = not args.sort_only
    plan = plan_sorting(files, rename=rename)

    # Print the plan
    print_plan(plan, dry_run=args.dry_run)
    print_rename_map(plan)

    if args.dry_run:
        print("\n💡 This was a dry run. To execute, run:")
        if api_key:
            print(f"  python3 neocities_sort.py --execute")
        else:
            print(f"  export NEOCITIES_API_KEY='{api_key}'  # or use username/password")
            print(f"  python3 neocities_sort.py --execute")
        print(f"\n  Or with HTML reference updates:")
        print(f"  python3 neocities_sort.py --execute --update-html")
        print(f"\n  Or sort-only (no renaming):")
        print(f"  python3 neocities_sort.py --execute --sort-only")
        return

    # Execute the plan
    print(f"\n🚀 Executing sorting plan...")
    execute_plan(api, plan)

    # Optionally update HTML references
    if args.update_html:
        html_dir = args.html_dir or str(Path.home())
        print(f"\n📝 Updating HTML references in {html_dir}...")
        update_html_references(html_dir, RENAME_MAP_FILE)

    print(f"\n✅ All done! Check your Neocities dashboard at https://{SITE_NAME}.neocities.org")


if __name__ == "__main__":
    main()
