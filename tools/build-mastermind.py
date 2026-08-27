#!/usr/bin/env python3
"""
Build the /mastermind-jacket page images from the camera originals.

Sources live in mastermind-jacket/ (untracked working folder). Each is copied
to _originals/mastermind-jacket/ before anything is written, then resized to
the site standard: 2000px on the long edge, progressive JPEG quality 85.

    python3 tools/build-mastermind.py

Files named *_preview1000.jpg are the low-res stand-ins that were in the folder
before the originals were restored. The script prefers a full-res source and
warns loudly if it has to fall back to one of those.
"""
import os
import shutil
from PIL import Image, ImageOps

LONG_EDGE = 2000
QUALITY = 85

#  output name                     camera original      preview fallback
SPEC = [
    ("mastermind-jacket-worn.jpg",   "0Y7A0067.JPG", ""),
    ("mastermind-jacket-collar.jpg", "0Y7A0017.JPG", "0Y7A0017_preview1000.jpg"),
    ("mastermind-jacket-button.jpg", "0Y7A0005.JPG", "0Y7A0005_preview1000.jpg"),
    # Cut from the edit 2026-08-27, deliberately not rebuilt:
    #   0Y7A0019 back-panel macro - the graphic already reads in the loop, the
    #     on-body frame and the studio wide; a fourth look added nothing.
    #   0Y7A0013 patch macro - same patch as the collar frame, and the button
    #     macro already carries the tight-detail slot.
    # Both derivatives live in _originals/mastermind-jacket/cut-from-edit/.
    # Closing frame: black-and-white studio wide, shot on a different body.
    ("mastermind-jacket-studio.jpg", "1786833202000_R0001080.JPG", ""),
]

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(root)
SRC_DIR = "mastermind-jacket"
OUT_DIR = "images/mastermind-jacket"
BAK_DIR = "_originals/mastermind-jacket"
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(BAK_DIR, exist_ok=True)

print(f"{'output':<34}{'size':>13}{'KB':>8}   source")
degraded = []
for out_name, original, fallback in SPEC:
    src = os.path.join(SRC_DIR, original)
    using_fallback = not os.path.exists(src)
    if using_fallback:
        src = os.path.join(SRC_DIR, fallback) if fallback else src
        if not fallback or not os.path.exists(src):
            print(f"{out_name:<34}{'MISSING':>13}   no source found")
            continue
        degraded.append(out_name)

    # Back the source up before writing anything derived from it.
    bak = os.path.join(BAK_DIR, os.path.basename(src))
    if not os.path.exists(bak):
        shutil.copy2(src, bak)

    # exif_transpose first: 0Y7A0067 is a portrait frame stored landscape with
    # Orientation=8. Reading the pixels without honouring that tag ships it
    # rotated 90 degrees, and the long-edge maths below picks the wrong edge.
    im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
    W, H = im.size
    scale = min(1.0, LONG_EDGE / max(W, H))     # never upscale
    size = (round(W * scale), round(H * scale))
    im = im.resize(size, Image.LANCZOS) if scale < 1.0 else im

    out = os.path.join(OUT_DIR, out_name)
    im.save(out, "JPEG", quality=QUALITY, optimize=True, progressive=True)
    kb = os.path.getsize(out) / 1024
    flag = "  <- LOW-RES STAND-IN" if using_fallback else ""
    print(f"{out_name:<34}{f'{size[0]}x{size[1]}':>13}{kb:>8.0f}   {os.path.basename(src)}{flag}")

if degraded:
    print("\nWARNING: built from 1000px stand-ins, not the originals:")
    for n in degraded:
        print(f"  {n}")
    print("Drop the full-res .JPG files into mastermind-jacket/ and re-run.")
print("\nSet width/height on the <img> tags in mastermind-jacket/index.html "
      "to the sizes printed above.")
