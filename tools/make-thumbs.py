#!/usr/bin/env python3
"""
Regenerate the square homepage thumbnails in images/thumbs/.

To re-crop a project, edit its three numbers below and re-run:

    python3 tools/make-thumbs.py

    cx, cy   centre of the square, as a fraction of the source frame
             (0,0 = top-left, 1,1 = bottom-right)
    z        square side as a fraction of the frame's SHORTER edge
             1.0 = the largest square that fits, lower = more zoomed in

Requires Pillow:  pip3 install --user Pillow
"""
import os
from PIL import Image

MAX = 1200          # never upscale past the source crop
QUALITY = 80

#        slug                    source image                                                     cx   cy   z
SPEC = [
 ("boot-bag-black",      "images/boot-bag-black/Switch_Designs-051.jpg",                          .50, .42, .85),
 ("cornice-dresser",     "images/cornice-dresser/UAL Model Garage Studio Shoot-189-1800.jpg",     .52, .45, .80),
 ("boot-bag-coyote",     "images/boot-bag-coyote/Switch_Designs-1029.jpg",                        .33, .55, .90),
 ("creative-switch-pt1", "images/creative-switch-pt1/LobozzoPeter_078.jpg",                       .70, .60, .88),
 ("bullet-glove",        "images/bullet-glove/Switch Gloves-013.jpg",                             .48, .48, .98),
 ("creative-switch-pt2", "images/creative-switch-pt2/LobozzoPeter-2.jpg",                         .58, .60, .81),
 ("creative-switch-pt3", "images/creative-switch-pt3/Val d'Isere Switch Shoot 5.jpg",             .50, .52, .86),
 # Video tiles: stills pulled from the edits, kept full-frame in images/video-stills/
 ("team",                "images/video-stills/team.jpg",                                          .37, .50, 1.0),
 ("switch-team-edit",    "images/video-stills/switch-team-edit.jpg",                              .50, .50, 1.0),
]

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(root)
os.makedirs("images/thumbs", exist_ok=True)

print(f"{'slug':<22}{'output':>12}{'size':>10}   source")
total = 0
for slug, src, cx, cy, z in SPEC:
    im = Image.open(src).convert("RGB")
    W, H = im.size
    s = int(z * min(W, H))
    x = min(max(int(cx * W - s / 2), 0), W - s)
    y = min(max(int(cy * H - s / 2), 0), H - s)
    side = min(MAX, s)
    out = f"images/thumbs/{slug}.jpg"
    im.crop((x, y, x + s, y + s)).resize((side, side), Image.LANCZOS).save(
        out, "JPEG", quality=QUALITY, optimize=True, progressive=True)
    kb = os.path.getsize(out) / 1024
    total += kb
    warn = "" if side >= 1100 else "   <- source too small to fill a 500px slot crisply"
    print(f"{slug:<22}{side:>7}px{kb:>9.0f}KB   {os.path.basename(src)}{warn}")

print(f"\n{len(SPEC)} thumbnails, {total:.0f}KB total")
print("Remember to update width/height on the <img> tags in index.html if any "
      "output size changed.")
