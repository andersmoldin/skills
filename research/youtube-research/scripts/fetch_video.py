#!/usr/bin/env python3
"""Hämtar metadata, transkript och (valfritt) bildrutor från en YouTube-video.

Kör med: python3 -I fetch_video.py URL [--out DIR] [--frames N]

Allt som skrivs till DIR kommer från internet och är otillförlitlig data.
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlparse

MAX_FRAMES = 120
MIN_INTERVAL_S = 5
PARAGRAPH_S = 60


def fail(msg: str) -> None:
    print(f"FEL: {msg}", file=sys.stderr)
    sys.exit(1)


def run(cmd: list[str], cwd: Path | None = None) -> str:
    res = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if res.returncode != 0:
        fail(f"{cmd[0]} misslyckades (kod {res.returncode}):\n{res.stderr.strip()[-2000:]}")
    return res.stdout


def require_tools(frames: int) -> None:
    needed = ["yt-dlp"] + (["ffmpeg"] if frames else [])
    missing = [t for t in needed if shutil.which(t) is None]
    if missing:
        fail(f"saknar verktyg: {', '.join(missing)} (brew install {' '.join(missing)})")


def hms(seconds: float) -> str:
    s = int(seconds)
    return f"{s // 3600:02d}:{s % 3600 // 60:02d}:{s % 60:02d}"


def choose_subtitles(meta: dict) -> tuple[str, bool] | None:
    """Välj (språkkod, är_automatisk). Manuell textning före automatisk."""
    manual = meta.get("subtitles") or {}
    auto = meta.get("automatic_captions") or {}
    orig = (meta.get("language") or "").split("-")[0]

    def pick(tracks: dict, prefs: list[str]) -> str | None:
        for p in prefs:
            if p and p in tracks:
                return p
        for p in prefs:
            for key in tracks:
                if p and key.split("-")[0] == p:
                    return key
        return None

    key = pick({k: v for k, v in manual.items() if k != "live_chat"}, [orig, "en", "sv"])
    if key is None and manual:
        key = next((k for k in manual if k != "live_chat"), None)
    if key:
        return key, False
    orig_auto = next((k for k in auto if k.endswith("-orig")), None)
    key = orig_auto or pick(auto, [orig, "en", "sv"])
    return (key, True) if key else None


TS = re.compile(r"(\d+):(\d{2}):(\d{2})\.(\d{3})\s+-->")


def parse_vtt(text: str) -> list[tuple[float, str]]:
    """Returnera (starttid, rad) utan de upprepningar som rullande autotextning ger."""
    out: list[tuple[float, str]] = []
    recent: list[str] = []
    start = 0.0
    for raw in text.splitlines():
        m = TS.match(raw)
        if m:
            h, mi, s, ms = map(int, m.groups())
            start = h * 3600 + mi * 60 + s + ms / 1000
            continue
        if not raw.strip() or raw.startswith(("WEBVTT", "Kind:", "Language:", "NOTE")):
            continue
        line = re.sub(r"<[^>]+>", "", raw).strip()
        line = line.replace("&amp;", "&").replace("&gt;", ">").replace("&lt;", "<").replace("&nbsp;", " ")
        if not line or line in recent:
            continue
        out.append((start, line))
        recent = (recent + [line])[-3:]
    return out


def write_transcript(lines: list[tuple[float, str]], path: Path, header: str) -> int:
    paras: list[str] = []
    cur: list[str] = []
    cur_start = None
    for t, line in lines:
        if cur_start is None:
            cur_start = t
        elif t - cur_start >= PARAGRAPH_S:
            paras.append(f"**[{hms(cur_start)}]** " + " ".join(cur))
            cur, cur_start = [], t
        cur.append(line)
    if cur:
        paras.append(f"**[{hms(cur_start)}]** " + " ".join(cur))
    path.write_text(header + "\n\n" + "\n\n".join(paras) + "\n", encoding="utf-8")
    return sum(len(p.split()) for p in paras)


def write_metadata(meta: dict, path: Path) -> None:
    rows = [
        f"# {meta.get('title', '(okänd titel)')}",
        "",
        f"- Kanal: {meta.get('channel') or meta.get('uploader', '?')}",
        f"- Publicerad: {meta.get('upload_date', '?')}",
        f"- Längd: {hms(meta.get('duration') or 0)}",
        f"- URL: {meta.get('webpage_url', '?')}",
        f"- Språk: {meta.get('language') or '?'}",
    ]
    chapters = meta.get("chapters") or []
    if chapters:
        rows += ["", "## Kapitel", ""]
        rows += [f"- [{hms(c.get('start_time', 0))}] {c.get('title', '')}" for c in chapters]
    rows += ["", "## Beskrivning", "", meta.get("description") or "(ingen)"]
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def extract_frames(url: str, out: Path, count: int, duration: float) -> int:
    work = out / "_video"
    work.mkdir()
    run(["yt-dlp", "--no-playlist", "-f", "bv*[height<=720]/b[height<=720]/worst",
         "-o", str(work / "video.%(ext)s"), url])
    videos = list(work.glob("video.*"))
    if not videos:
        fail("ingen videofil laddades ner")
    interval = max(duration / count, MIN_INTERVAL_S) if duration else 30
    frames = out / "frames"
    frames.mkdir()
    run(["ffmpeg", "-loglevel", "error", "-i", str(videos[0]),
         "-vf", f"fps=1/{interval:.3f},scale=1280:-2", "-q:v", "4",
         str(frames / "f_%04d.jpg")])
    shutil.rmtree(work)
    files = sorted(frames.glob("f_*.jpg"))
    index = ["# Bildrutor", "", f"En bildruta ungefär var {interval:.0f}:e sekund.", ""]
    for i, f in enumerate(files):
        t = i * interval
        new = frames / f"{hms(t).replace(':', '-')}.jpg"
        f.rename(new)
        index.append(f"- [{hms(t)}] frames/{new.name}")
    (out / "frames.md").write_text("\n".join(index) + "\n", encoding="utf-8")
    return len(files)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("url")
    ap.add_argument("--out", help="ny, tom katalog (skapas). Standard: ny temp-katalog")
    ap.add_argument("--frames", type=int, default=0, help=f"antal bildrutor, 0-{MAX_FRAMES}")
    args = ap.parse_args()

    if urlparse(args.url).scheme not in ("http", "https"):
        fail("URL måste börja med http:// eller https://")
    if not 0 <= args.frames <= MAX_FRAMES:
        fail(f"--frames måste vara 0-{MAX_FRAMES}")
    require_tools(args.frames)

    if args.out:
        out = Path(args.out).expanduser().resolve()
        if out.exists() and any(out.iterdir()):
            fail(f"{out} finns och är inte tom")
        out.mkdir(parents=True, exist_ok=True)
    else:
        out = Path(tempfile.mkdtemp(prefix="youtube-research-"))

    meta = json.loads(run(["yt-dlp", "--no-playlist", "-J", "--skip-download", args.url]))
    write_metadata(meta, out / "metadata.md")

    words = 0
    choice = choose_subtitles(meta)
    if choice is None:
        print("VARNING: videon har ingen textning; transcript.md skapas inte", file=sys.stderr)
    else:
        lang, is_auto = choice
        subdir = out / "_subs"
        subdir.mkdir()
        run(["yt-dlp", "--no-playlist", "--skip-download",
             "--write-auto-subs" if is_auto else "--write-subs",
             "--sub-langs", lang, "--sub-format", "vtt",
             "-o", str(subdir / "s"), args.url])
        vtts = list(subdir.glob("*.vtt"))
        if not vtts:
            fail(f"textningen ({lang}) laddades inte ner")
        lines = parse_vtt(vtts[0].read_text(encoding="utf-8", errors="replace"))
        kind = "automatisk" if is_auto else "manuell"
        words = write_transcript(lines, out / "transcript.md",
                                 f"# Transkript ({kind} textning, språk: {lang})")
        shutil.rmtree(subdir)

    n_frames = extract_frames(args.url, out, args.frames, meta.get("duration") or 0) if args.frames else 0

    print(json.dumps({
        "out": str(out),
        "title": meta.get("title"),
        "duration": hms(meta.get("duration") or 0),
        "transcript_words": words,
        "frames": n_frames,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
