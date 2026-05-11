from __future__ import annotations

from pathlib import Path
from typing import Any, Sequence

from PIL import Image

# Pillow compatibility: ADAPTIVE may not exist in some stubs.
_ADAPTIVE_RESAMPLING = getattr(Image, "ADAPTIVE", None)
if _ADAPTIVE_RESAMPLING is None:
    _ADAPTIVE_RESAMPLING = Image.Resampling.LANCZOS

# Pylance: `palette=` attend un type "Palette". En pratique, Pillow accepte
# Image.ADAPTIVE (ou une valeur équivalente). On caste pour désactiver le faux positif.
_PALETTE_VALUE: Any = _ADAPTIVE_RESAMPLING


def export_frames_to_gif(
    frames: Sequence[Image.Image],
    output_path: str | Path,
    *,
    fps: int,
    color_count: int,
    loop_mode: str,
    loop_count: int,
    disposal: int = 2,
    optimize: bool = False,
) -> None:
    """
    Exporte une séquence de frames PIL (RGB/anything convertissable) en GIF.

    - Conversion en palette (mode "P") avec palette adaptative
    - Duration = 1000/fps
    - loop: 0 si loop_mode == "infini", sinon loop_count
    """
    if not frames:
        raise ValueError("export_frames_to_gif: 'frames' est vide")

    if fps <= 0:
        raise ValueError("export_frames_to_gif: 'fps' doit être > 0")

    if color_count <= 0:
        raise ValueError("export_frames_to_gif: 'color_count' doit être > 0")

    # Conversion palette
    p_frames: list[Image.Image] = []
    for frame in frames:
        p_frames.append(
            frame.convert(
                "P",
                palette=_PALETTE_VALUE,
                colors=color_count,
                dither=Image.Dither.NONE,
            )
        )

    loop = 0 if str(loop_mode) == "infini" else int(loop_count)

    duration_ms = int(1000 / fps)

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    p_frames[0].save(
        str(out),
        save_all=True,
        append_images=p_frames[1:],
        duration=duration_ms,
        loop=loop,
        disposal=disposal,
        optimize=optimize,
    )
