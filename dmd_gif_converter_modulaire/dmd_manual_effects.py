from __future__ import annotations

import math
import random
from typing import List, Tuple

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

from .dmd_engine import DMDEngine


class ManualEffects:
    """Collection d'effets avancés pour l'édition manuelle."""

    @staticmethod
    def scroll_effect(
        img: Image.Image,
        direction: str = "horizontal",
        speed: int = 2,
        duration: float = 2.0,
        fps: int = 10,
    ) -> List[Image.Image]:
        """Scroll classique (liste de frames)."""
        return DMDEngine.create_animation_frames(
            img,
            {
                "direction": direction,
                "scroll_speed": speed,
                "duration": duration,
                "fps": fps,
            },
            bg_color=(0, 0, 0),
        )[0]

    @staticmethod
    def fade_effect(
        img: Image.Image,
        duration: float = 2.0,
        fps: int = 10,
        fade_in: bool = True,
    ) -> List[Image.Image]:
        """Fade in/out."""
        frames: List[Image.Image] = []
        num_frames = int(fps * duration)

        for i in range(num_frames):
            alpha = i / num_frames if fade_in else 1 - (i / num_frames)
            frame = img.copy()

            enhancer = ImageEnhance.Brightness(frame)
            frame = enhancer.enhance(alpha)

            canvas = Image.new("RGB", (128, 32), (0, 0, 0))
            w, h = frame.size
            x, y = (128 - w) // 2, (32 - h) // 2
            canvas.paste(frame, (x, y))
            frames.append(canvas)

        return frames

    @staticmethod
    def zoom_effect(
        img: Image.Image,
        duration: float = 2.0,
        fps: int = 10,
        zoom_in: bool = True,
    ) -> List[Image.Image]:
        """Zoom in/out."""
        frames: List[Image.Image] = []
        num_frames = int(fps * duration)

        for i in range(num_frames):
            progress = i / num_frames
            scale = 0.5 + progress * 0.5 if zoom_in else 1.0 - progress * 0.5

            w, h = img.size
            new_w, new_h = int(w * scale), int(h * scale)
            scaled = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

            canvas = Image.new("RGB", (128, 32), (0, 0, 0))
            x, y = (128 - new_w) // 2, (32 - new_h) // 2
            canvas.paste(scaled, (x, y))
            frames.append(canvas)

        return frames

    @staticmethod
    def rotate_effect(
        img: Image.Image, duration: float = 2.0, fps: int = 10
    ) -> List[Image.Image]:
        """Rotation 360°."""
        frames: List[Image.Image] = []
        num_frames = int(fps * duration)

        for i in range(num_frames):
            angle = (i / num_frames) * 360
            rotated = img.rotate(angle, expand=True, fillcolor=(0, 0, 0))

            canvas = Image.new("RGB", (128, 32), (0, 0, 0))
            w, h = rotated.size
            x, y = (128 - w) // 2, (32 - h) // 2
            canvas.paste(rotated, (x, y))
            frames.append(canvas)

        return frames

    @staticmethod
    def wave_effect(
        img: Image.Image,
        duration: float = 2.0,
        fps: int = 10,
        amplitude: int = 5,
    ) -> List[Image.Image]:
        """Effet vague."""
        frames: List[Image.Image] = []
        num_frames = int(fps * duration)
        w, h = img.size

        for i in range(num_frames):
            phase = (i / num_frames) * 2 * math.pi
            arr = np.array(img)
            result = np.zeros_like(arr)

            for y in range(h):
                offset = int(amplitude * math.sin(phase + y * 0.5))
                for x in range(w):
                    new_x = (x + offset) % w
                    result[y, x] = arr[y, new_x]

            frame = Image.fromarray(result)
            canvas = Image.new("RGB", (128, 32), (0, 0, 0))
            canvas.paste(frame, ((128 - w) // 2, (32 - h) // 2))
            frames.append(canvas)

        return frames

    @staticmethod
    def bounce_effect(
        img: Image.Image, duration: float = 2.0, fps: int = 10
    ) -> List[Image.Image]:
        """Rebond."""
        frames: List[Image.Image] = []
        num_frames = int(fps * duration)

        for i in range(num_frames):
            progress = i / num_frames
            y_offset = int(abs(math.sin(progress * math.pi * 2)) * 10)

            canvas = Image.new("RGB", (128, 32), (0, 0, 0))
            w, h = img.size
            x = (128 - w) // 2
            y = (32 - h) // 2 - y_offset
            canvas.paste(img, (x, y))
            frames.append(canvas)

        return frames

    @staticmethod
    def flash_effect(
        img: Image.Image,
        duration: float = 1.0,
        fps: int = 10,
        flashes: int = 3,
    ) -> List[Image.Image]:
        """Flash stroboscopique."""
        frames: List[Image.Image] = []
        num_frames = int(fps * duration)
        flash_interval = num_frames // (flashes * 2) if flashes > 0 else num_frames

        for i in range(num_frames):
            is_flash = (i // flash_interval) % 2 == 0 if flash_interval > 0 else True

            canvas = Image.new(
                "RGB",
                (128, 32),
                (255, 255, 255) if is_flash else (0, 0, 0),
            )
            if not is_flash:
                w, h = img.size
                canvas.paste(img, ((128 - w) // 2, (32 - h) // 2))
            frames.append(canvas)

        return frames

    @staticmethod
    def slide_effect(
        img: Image.Image,
        direction: str = "left",
        duration: float = 1.0,
        fps: int = 10,
    ) -> List[Image.Image]:
        """Slide depuis un côté."""
        frames: List[Image.Image] = []
        num_frames = int(fps * duration)
        w, h = img.size

        for i in range(num_frames):
            progress = i / num_frames
            canvas = Image.new("RGB", (128, 32), (0, 0, 0))

            if direction == "left":
                x = int(-w + progress * (128 + w)) - 128 // 2
                y = (32 - h) // 2
            elif direction == "right":
                x = int(128 - progress * (128 + w)) + 128 // 2
                y = (32 - h) // 2
            elif direction == "top":
                x = (128 - w) // 2
                y = int(-h + progress * (32 + h)) - 32 // 2
            else:  # bottom
                x = (128 - w) // 2
                y = int(32 - progress * (32 + h)) + 32 // 2

            canvas.paste(img, (x, y))
            frames.append(canvas)

        return frames

    @staticmethod
    def spiral_effect(
        img: Image.Image, duration: float = 2.0, fps: int = 10
    ) -> List[Image.Image]:
        """Spirale."""
        frames: List[Image.Image] = []
        num_frames = int(fps * duration)

        for i in range(num_frames):
            progress = i / num_frames
            angle = progress * 360 * 2
            scale = 0.3 + progress * 0.7

            w, h = img.size
            new_w, new_h = int(w * scale), int(h * scale)
            scaled = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            rotated = scaled.rotate(angle, expand=True, fillcolor=(0, 0, 0))

            canvas = Image.new("RGB", (128, 32), (0, 0, 0))
            rw, rh = rotated.size
            canvas.paste(rotated, ((128 - rw) // 2, (32 - rh) // 2))
            frames.append(canvas)

        return frames

    @staticmethod
    def shake_effect(
        img: Image.Image,
        duration: float = 1.0,
        fps: int = 10,
        intensity: int = 5,
    ) -> List[Image.Image]:
        """Tremblement."""
        frames: List[Image.Image] = []
        num_frames = int(fps * duration)

        for i in range(num_frames):
            x_offset = random.randint(-intensity, intensity)
            y_offset = random.randint(-intensity, intensity)

            canvas = Image.new("RGB", (128, 32), (0, 0, 0))
            w, h = img.size
            x = (128 - w) // 2 + x_offset
            y = (32 - h) // 2 + y_offset
            canvas.paste(img, (x, y))
            frames.append(canvas)

        return frames

    @staticmethod
    def pulse_effect(
        img: Image.Image, duration: float = 2.0, fps: int = 10
    ) -> List[Image.Image]:
        """Pulsation."""
        frames: List[Image.Image] = []
        num_frames = int(fps * duration)

        for i in range(num_frames):
            progress = i / num_frames
            scale = 0.8 + 0.4 * abs(math.sin(progress * math.pi * 2))

            w, h = img.size
            new_w, new_h = int(w * scale), int(h * scale)
            scaled = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

            canvas = Image.new("RGB", (128, 32), (0, 0, 0))
            canvas.paste(scaled, ((128 - new_w) // 2, (32 - new_h) // 2))
            frames.append(canvas)

        return frames

    @staticmethod
    def glitch_effect(
        img: Image.Image, duration: float = 1.0, fps: int = 10
    ) -> List[Image.Image]:
        """Effet glitch."""
        frames: List[Image.Image] = []
        num_frames = int(fps * duration)
        arr = np.array(img)

        for i in range(num_frames):
            if random.random() < 0.3:
                glitched = arr.copy()

                shift = random.randint(5, 15)
                glitched[:, :, 0] = np.roll(glitched[:, :, 0], shift, axis=1)
                glitched[:, :, 2] = np.roll(glitched[:, :, 2], -shift, axis=1)

                frame = Image.fromarray(glitched)
            else:
                frame = img.copy()

            canvas = Image.new("RGB", (128, 32), (0, 0, 0))
            w, h = frame.size
            canvas.paste(frame, ((128 - w) // 2, (32 - h) // 2))
            frames.append(canvas)

        return frames

    @staticmethod
    def pixelate_effect(
        img: Image.Image, duration: float = 2.0, fps: int = 10
    ) -> List[Image.Image]:
        """Pixelisation progressive."""
        frames: List[Image.Image] = []
        num_frames = int(fps * duration)

        for i in range(num_frames):
            progress = i / num_frames
            pixel_size = int(1 + progress * 10)

            w, h = img.size
            small = img.resize(
                (w // pixel_size, h // pixel_size), Image.Resampling.NEAREST
            )
            pixelated = small.resize((w, h), Image.Resampling.NEAREST)

            canvas = Image.new("RGB", (128, 32), (0, 0, 0))
            canvas.paste(pixelated, ((128 - w) // 2, (32 - h) // 2))
            frames.append(canvas)

        return frames

    @staticmethod
    def blur_transition_effect(
        img: Image.Image,
        duration: float = 2.0,
        fps: int = 10,
    ) -> List[Image.Image]:
        """Transition floue."""
        frames: List[Image.Image] = []
        num_frames = int(fps * duration)

        for i in range(num_frames):
            progress = i / num_frames
            radius = int(progress * 10)

            blurred = (
                img.filter(ImageFilter.GaussianBlur(radius=radius))
                if radius > 0
                else img.copy()
            )

            canvas = Image.new("RGB", (128, 32), (0, 0, 0))
            w, h = blurred.size
            canvas.paste(blurred, ((128 - w) // 2, (32 - h) // 2))
            frames.append(canvas)

        return frames

    @staticmethod
    def color_shift_effect(
        img: Image.Image,
        duration: float = 2.0,
        fps: int = 10,
    ) -> List[Image.Image]:
        """Décalage de couleurs."""
        frames: List[Image.Image] = []
        num_frames = int(fps * duration)
        arr = np.array(img)

        for i in range(num_frames):
            progress = i / num_frames
            angle = progress * 360

            shifted = arr.copy()
            hsv = Image.fromarray(shifted).convert("HSV")
            h, s, v = hsv.split()

            h_arr = np.array(h)
            h_arr = (h_arr + int(angle)) % 256
            h = Image.fromarray(h_arr.astype("uint8"))

            shifted_img = Image.merge("HSV", (h, s, v)).convert("RGB")

            canvas = Image.new("RGB", (128, 32), (0, 0, 0))
            w, h = shifted_img.size
            canvas.paste(shifted_img, ((128 - w) // 2, (32 - h) // 2))
            frames.append(canvas)

        return frames
