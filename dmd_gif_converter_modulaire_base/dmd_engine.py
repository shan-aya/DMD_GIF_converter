from __future__ import annotations

from typing import Any, Dict, List, Tuple

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter


class DMDEngine:
    """Moteur de rendu optimisé pour écrans DMD avec algorithmes adaptatifs."""

    @staticmethod
    def ensure_rgb_on_black(img: Image.Image) -> Image.Image:
        """Convertit une image en RGB en compositant la transparence sur noir."""
        if img.mode in ("RGBA", "LA") or img.info.get("transparency") is not None:
            img_rgba = img.convert("RGBA")
            background = Image.new("RGB", img_rgba.size, (0, 0, 0))
            background.paste(img_rgba, mask=img_rgba.split()[-1])
            return background
        return img.convert("RGB")

    @staticmethod
    def detect_background_color(img: Image.Image) -> Tuple[Tuple[int, int, int], bool]:
        """
        Détecte la couleur de fond en analysant les coins de l'image.
        Retourne: (couleur_rgb, est_sombre)
        """
        arr = np.array(DMDEngine.ensure_rgb_on_black(img))
        h, w = arr.shape[:2]

        corner_size = min(10, min(h, w) // 8)
        corners = np.concatenate(
            [
                arr[:corner_size, :corner_size].reshape(-1, 3),
                arr[:corner_size, -corner_size:].reshape(-1, 3),
                arr[-corner_size:, :corner_size].reshape(-1, 3),
                arr[-corner_size:, -corner_size:].reshape(-1, 3),
            ]
        )

        bg_candidate = np.median(corners, axis=0).astype(int)

        if np.mean(bg_candidate) < 40:
            return (0, 0, 0), True

        dist_to_black = np.sqrt(np.sum(bg_candidate**2))
        if dist_to_black < 80:
            return (0, 0, 0), True

        return (int(bg_candidate[0]), int(bg_candidate[1]), int(bg_candidate[2])), False

    @staticmethod
    def detect_palette(
        img: Image.Image, max_colors: int = 16
    ) -> List[Tuple[int, int, int]]:
        """
        Détecte les couleurs dominantes de l'image.
        Retourne: liste de couleurs RGB triées par fréquence.
        """
        img_small = img.resize((128, 128), Image.Resampling.LANCZOS)
        arr = np.array(img_small.convert("RGB"))
        pixels = arr.reshape(-1, 3)

        quantized = (pixels // 32) * 32
        unique, counts = np.unique(quantized, axis=0, return_counts=True)

        sorted_indices = np.argsort(-counts)

        palette: List[Tuple[int, int, int]] = []
        for i in sorted_indices[:max_colors]:
            rgb = unique[i]
            palette.append((int(rgb[0]), int(rgb[1]), int(rgb[2])))

        return palette

    @staticmethod
    def optimize_for_dmd(img: Image.Image, settings: Dict[str, Any]) -> Image.Image:
        """Optimise l'image pour affichage DMD."""
        img = DMDEngine.ensure_rgb_on_black(img)

        if "brightness" in settings and settings["brightness"] != 1.0:
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(float(settings["brightness"]))

        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(float(settings.get("contrast", 1.5)))

        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(float(settings.get("saturation", 1.3)))

        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.2)

        arr = np.array(img)
        black_threshold = int(settings.get("black_threshold", 30))
        mask = np.all(arr < black_threshold, axis=2)
        arr[mask] = [0, 0, 0]

        img = Image.fromarray(arr)
        img = img.filter(ImageFilter.MedianFilter(size=3))

        return img

    @staticmethod
    def adaptive_resize(
        img: Image.Image,
        target_w: int = 128,
        target_h: int = 32,
        mode: str = "auto",
        pixel_perfect: bool = False,
    ) -> Tuple[Image.Image, int, int]:
        """
        Redimensionnement adaptatif pour DMD.
        """
        w, h = img.size

        if mode == "auto":
            ratio = w / h
            target_ratio = target_w / target_h
            mode = "fit" if abs(ratio - target_ratio) < 0.5 else "fill"

        if mode == "fit":
            scale = min(target_w / w, target_h / h)
        else:
            scale = max(target_w / w, target_h / h)

        new_w = int(w * scale)
        new_h = int(h * scale)

        resample = (
            Image.Resampling.NEAREST if pixel_perfect else Image.Resampling.LANCZOS
        )
        img = img.resize((new_w, new_h), resample)
        return img, new_w, new_h

    @staticmethod
    def create_animation_frames(
        img: Image.Image,
        settings: Dict[str, Any],
        bg_color: Tuple[int, int, int] = (0, 0, 0),
        cleanup: bool = False,
        cleanup_power: float = 1.0,
    ) -> Tuple[List[Image.Image], str]:
        """
        Génère les frames d'animation selon direction et paramètres.
        Retourne: (frames, direction_effective)
        """
        w, h = img.size
        direction = str(settings["direction"])
        fps = int(settings["fps"])
        scroll_speed = int(settings["scroll_speed"])
        duration = float(settings.get("duration", 2.0))

        if direction == "auto":
            if w > 128 and h <= 32:
                direction = "horizontal"
            elif h > 32 and w <= 128:
                direction = "vertical"
            elif w > 128 and h > 32:
                direction = "horizontal" if (w - 128) > (h - 32) else "vertical"
            else:
                direction = "static"

        frames: List[Image.Image] = []

        if direction == "static" or (w <= 128 and h <= 32):
            canvas = Image.new("RGB", (128, 32), bg_color)
            x = (128 - w) // 2
            y = (32 - h) // 2
            canvas.paste(img, (x, y))
            if cleanup:
                canvas = DMDEngine.cleanup_dmd_frame(canvas, cleanup_power)
            num_frames = max(int(fps * duration), 1)
            frames = [canvas] * num_frames

        elif direction == "horizontal":
            max_offset = max(0, w - 128)
            y = (32 - h) // 2

            for offset in range(0, max_offset + 1, scroll_speed):
                canvas = Image.new("RGB", (128, 32), bg_color)
                canvas.paste(img, (-offset, y))
                if cleanup:
                    canvas = DMDEngine.cleanup_dmd_frame(canvas, cleanup_power)
                frames.append(canvas)

            for offset in range(max_offset, -1, -scroll_speed):
                canvas = Image.new("RGB", (128, 32), bg_color)
                canvas.paste(img, (-offset, y))
                if cleanup:
                    canvas = DMDEngine.cleanup_dmd_frame(canvas, cleanup_power)
                frames.append(canvas)

        elif direction == "vertical":
            max_offset = max(0, h - 32)
            x = (128 - w) // 2

            for offset in range(0, max_offset + 1, scroll_speed):
                canvas = Image.new("RGB", (128, 32), bg_color)
                canvas.paste(img, (x, -offset))
                if cleanup:
                    canvas = DMDEngine.cleanup_dmd_frame(canvas, cleanup_power)
                frames.append(canvas)

            for offset in range(max_offset, -1, -scroll_speed):
                canvas = Image.new("RGB", (128, 32), bg_color)
                canvas.paste(img, (x, -offset))
                if cleanup:
                    canvas = DMDEngine.cleanup_dmd_frame(canvas, cleanup_power)
                frames.append(canvas)

        else:
            canvas = Image.new("RGB", (128, 32), bg_color)
            canvas.paste(img, ((128 - w) // 2, (32 - h) // 2))
            frames = [canvas]

        if frames and len(frames) < fps * duration:
            multiplier = int((fps * duration) / len(frames)) + 1
            frames = frames * multiplier

        return (
            frames if frames else [Image.new("RGB", (128, 32), bg_color)]
        ), direction

    @staticmethod
    def cleanup_dmd_frame(img: Image.Image, power: float = 1.0) -> Image.Image:
        """Nettoie les pixels isolés sur le rendu DMD avec puissance variable."""
        if img.mode != "RGB":
            img = img.convert("RGB")

        if power <= 0:
            return img

        cleaned = img

        if power >= 0.3:
            cleaned = cleaned.filter(ImageFilter.MedianFilter(size=3))
        if power >= 0.6:
            cleaned = cleaned.filter(ImageFilter.ModeFilter(size=3))
        if power >= 0.9:
            cleaned = cleaned.filter(ImageFilter.MedianFilter(size=5))

        return cleaned
