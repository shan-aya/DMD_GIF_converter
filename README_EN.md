[🇫🇷 Français](./README.md) · 🇬🇧 **English** · [🇪🇸 Español](./README_ES.md)

DMD GIF Creator 128x32 - v3.0.1
Shan_ayA 2026

A complete application to create GIFs optimized for 128x32 DMD displays: from images
(automatic analysis and proposals), from a video, or from animated text, with advanced
manual editing.

(Formerly "DMD GIF Converter".)

## What's new in v3.0.1

- **Batch processing about 2.4 times faster**: up to 12 images processed in parallel
  depending on the CPU, and faster GIF encoding (one palette for the whole
  animation).
- **More complete translation**: status messages, information panels, proposal titles
  and file/color dialogs now follow the chosen language (English or Spanish).

## What's new in v3.0

- **VIDEO tab**: turns a section of a video (MP4, AVI, MOV, MKV) into a 128×32 GIF,
  with section selection, framing by automatic tracking, auto framing or manual points
  (area and zoom that change over time), and automatic quality.
- **HELP tab**: the full guide inside the application, in French, English or Spanish.
- **Drag and drop** images, folders or a video anywhere on the window.
- **LED preview** faithful to the panel render (magnifier, LED brightness) in every
  creation tab.
- **Parallel batch processing**, and very large folders (tens of thousands of images)
  loaded in a few seconds without freezing the window.
- **raw565** format accepted as input, undo/redo history in the MANUAL tab, help
  tooltips, reviewed FR/EN/ES translations.

Details (in French): [CHANGELOG_FR](./CHANGELOG_FR)

## Installation

**Windows**: download `dmd_gif_creator_v301.exe` from the
[latest Release](https://github.com/shan-aya/DMD_GIF_converter/releases/latest) and run
it — nothing to install.

**From the sources** ([`dmd_gif_creator/`](./dmd_gif_creator) folder):

    pip install pillow numpy tkinterdnd2 markdown opencv-contrib-python
    python dmd_gif_creator/dmd_gif_creator_v301.py

`opencv-contrib-python` (not `opencv-python`) is required for the automatic tracking of
the VIDEO tab; the two packages must not be installed at the same time.

## Screenshots (version 2.7)

<img width="1909" height="1079" alt="Screenshot 2026-04-29 150630" src="https://github.com/user-attachments/assets/5515fd66-c5e9-4370-939c-48becf656cae" />
<img width="1909" height="1079" alt="Screenshot 2026-04-29 150638" src="https://github.com/user-attachments/assets/c6892979-22fd-4854-8c5b-2cb591af6243" />
<img width="1909" height="1079" alt="Screenshot 2026-04-29 150929" src="https://github.com/user-attachments/assets/bd582c2c-f7c8-48e3-a1a3-f77a23da3d75" />
<img width="1908" height="1077" alt="Screenshot 2026-04-29 150940" src="https://github.com/user-attachments/assets/d43e075e-7286-4e7f-a94e-2866367303f7" />


## Documentation

The full user guide is available here:

- [Version Française 🇫🇷](./NOTICE_FR.md)
- [Versión en Español 🇪🇸](./NOTICE_ES.md)
- [English version EN](./NOTICE_EN.md)

Click the language of your choice to open the matching guide. The same guide is
available inside the application, **HELP** tab.


---

## 🤝 Thanks

- [RetroPixelLED original](https://github.com/fjgordillo86/RetroPixelLED)
- Visual Studio Code
- [Sixth](https://trysixth.com/)

## ☕ Support the project

If this project helped you, you can buy me a coffee:

👉 [☕ Donate via PayPal](https://www.paypal.com/paypalme/felysaya)

## Contact

For any question, suggestion or contribution, open an issue or contact the author Shan_ayA.

---

© 2026 Shan_ayA
