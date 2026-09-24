[🇫🇷 Français](./README.md) · 🇬🇧 **English** · [🇪🇸 Español](./README_ES.md)

# DMD GIF Creator 128x32 — v3.0.1

Create GIFs optimized for 128×32 DMD displays (arcade cabinet, pinball,
[RecalBox DMD](https://github.com/shan-aya/RecalBoxDMD)) from **images**, a **video**
or **animated text**, with automatic analysis, advanced manual editing and batch
processing of whole folders.

(Formerly "DMD GIF Converter".)

![AUTO tab](./screenshots/auto_en.png)

## Download

**Windows**: download `dmd_gif_creator_v301.exe` from the
[latest Release](https://github.com/shan-aya/DMD_GIF_converter/releases/latest) and run
it — nothing to install.

**From the sources** ([`dmd_gif_creator/`](./dmd_gif_creator) folder):

    pip install pillow numpy tkinterdnd2 markdown opencv-contrib-python
    python dmd_gif_creator/dmd_gif_creator_v301.py

`opencv-contrib-python` (not `opencv-python`) is required for the automatic tracking of
the VIDEO tab; the two packages must not be installed at the same time.

## What the application does

### AUTO — one image, six proposals

Drag and drop images or whole folders (PNG, JPG, BMP, GIF, raw565). For each image,
the application analyzes the content and offers six 128×32 renders: resized,
scrolling, optimized, and three artistic variants. The LED preview reproduces the
real panel render. **Batch processing** then converts the whole list in parallel,
keeping the folder tree, without ever modifying the source files.

### MANUAL — advanced editing

![MANUAL tab](./screenshots/manual_en.png)

128×32 crop, brightness, contrast, saturation, sharpness, filters, fill and magic
eraser, animations (scroll, zoom, fade…) with easing and looping, multi-images and
morphing, undo/redo history.

### VIDEO — a GIF from a video

![VIDEO tab](./screenshots/video_en.png)

Pick a section of a video (MP4, AVI, MOV, MKV) on the timeline, then the framing:
automatic subject tracking, auto framing with zoom, or manual points (area and zoom
that change over time). Automatic quality adjusts contrast, saturation and brightness
from the video, and the GIF size is estimated live.

### TEXTSCROLL — animated text

![TEXTSCROLL tab](./screenshots/textscroll_en.png)

Font, size, colors, text and color effects, and many animations (horizontal or
vertical scroll, wave, Star Wars, typewriter, Matrix rain, glitch…), with a duration
fitted automatically to the text length.

### Also

- **SETTINGS**: defaults, language (French, English, Spanish).
- **DEBUG**: detailed, filterable log.
- **HELP**: the full guide inside the application.

## What's new

**v3.0.1**
- Batch processing about **2.4 times faster**: up to 12 images in parallel depending
  on the CPU, and faster GIF encoding.
- More complete English and Spanish translation of the interface.

**v3.0**
- **VIDEO** tab, **HELP** tab, **drag and drop** anywhere on the window.
- **LED preview** in every creation tab.
- Parallel batch processing, folders of tens of thousands of images loaded without
  freezing the window.
- raw565 input format, undo/redo in MANUAL, help tooltips.

Full history (in French): [CHANGELOG_FR](./CHANGELOG_FR)

## Documentation

Full user guide: [🇫🇷 Français](./NOTICE_FR.md) · [🇬🇧 English](./NOTICE_EN.md) ·
[🇪🇸 Español](./NOTICE_ES.md) — also available inside the application, **HELP** tab.

---

## 🤝 Thanks

- [RetroPixelLED original](https://github.com/fjgordillo86/RetroPixelLED)
- Visual Studio Code
- [Sixth](https://trysixth.com/)

## ☕ Support the project

If this project helped you, you can buy me a coffee:
👉 [☕ Donate via PayPal](https://www.paypal.com/paypalme/felysaya)

## Contact

For any question, suggestion or contribution, open an issue or contact the author
Shan_ayA.

---

© 2026 Shan_ayA
