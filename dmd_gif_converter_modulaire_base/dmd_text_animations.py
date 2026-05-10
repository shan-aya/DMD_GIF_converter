from __future__ import annotations

import math
import random
from typing import Any, List

import numpy as np
from PIL import Image, ImageDraw


class TextAnimations:
    """Animations avancées pour texte défilant."""

    @staticmethod
    def scroll_wave(
        text_img: Image.Image, duration: float = 3.0, fps: int = 10
    ) -> List[Image.Image]:
        frames: List[Image.Image] = []
        num_frames = int(fps * duration)
        w, h = text_img.size

        for i in range(num_frames):
            progress = i / num_frames
            offset_x = int(progress * (w + 128))

            canvas = Image.new("RGB", (128, 32), (0, 0, 0))
            arr = np.array(text_img)
            result = np.zeros((32, 128, 3), dtype=np.uint8)

            for x in range(128):
                src_x = (x + offset_x) % w
                wave_y = int(5 * math.sin((x + offset_x) * 0.1))

                for y in range(32):
                    src_y = (y - wave_y) % 32
                    if src_x < w and src_y < h:
                        result[y, x] = arr[src_y, src_x]

            frames.append(Image.fromarray(result))

        return frames

    @staticmethod
    def starwars_scroll(
        text_img: Image.Image, duration: float = 5.0, fps: int = 10
    ) -> List[Image.Image]:
        frames: List[Image.Image] = []
        num_frames = int(fps * duration)
        w, h = text_img.size

        for i in range(num_frames):
            progress = i / num_frames
            canvas = Image.new("RGB", (128, 32), (0, 0, 0))

            for y in range(32):
                scale = 0.5 + (y / 32) * 0.5
                src_y = int((y + progress * 64) % h)

                scaled_w = int(128 * scale)
                x_offset = (128 - scaled_w) // 2

                for x in range(scaled_w):
                    src_x = int((x / scale) % w)
                    if src_x < w and src_y < h:
                        arr = np.array(text_img)
                        canvas.putpixel((x + x_offset, y), tuple(arr[src_y, src_x]))

            frames.append(canvas)

        return frames

    @staticmethod
    def bounce_scroll(
        text_img: Image.Image, duration: float = 3.0, fps: int = 10
    ) -> List[Image.Image]:
        frames: List[Image.Image] = []
        num_frames = int(fps * duration)
        w, h = text_img.size

        for i in range(num_frames):
            progress = i / num_frames
            offset_x = int(progress * (w + 128))
            bounce_y = int(abs(math.sin(progress * math.pi * 4)) * 10)

            canvas = Image.new("RGB", (128, 32), (0, 0, 0))

            for x in range(128):
                src_x = (x + offset_x) % w
                for y in range(32):
                    src_y = (y - bounce_y) % 32
                    if src_x < w and src_y < h:
                        arr = np.array(text_img)
                        canvas.putpixel((x, y), tuple(arr[src_y, src_x]))

            frames.append(canvas)

        return frames

    @staticmethod
    def typewriter(
        text: str,
        font: Any,
        color: tuple[int, int, int],
        bg_color: tuple[int, int, int],
        duration: float = 3.0,
        fps: int = 10,
    ) -> List[Image.Image]:
        frames: List[Image.Image] = []
        num_frames = int(fps * duration)
        chars_per_frame = max(1, len(text) // num_frames)

        for i in range(num_frames):
            visible_text = text[: i * chars_per_frame]

            img = Image.new("RGB", (500, 32), bg_color)
            draw = ImageDraw.Draw(img)
            draw.text((10, 8), visible_text, fill=color, font=font)

            canvas = Image.new("RGB", (128, 32), bg_color)
            canvas.paste(img.crop((0, 0, 128, 32)), (0, 0))
            frames.append(canvas)

        return frames

    @staticmethod
    def explode(
        text_img: Image.Image, duration: float = 2.0, fps: int = 10
    ) -> List[Image.Image]:
        frames: List[Image.Image] = []
        num_frames = int(fps * duration)
        w, h = text_img.size
        arr = np.array(text_img)

        pixels: list[tuple[int, int, np.ndarray]] = []
        for y in range(h):
            for x in range(w):
                if np.any(arr[y, x] > 10):
                    pixels.append((x, y, arr[y, x]))

        for i in range(num_frames):
            progress = i / num_frames
            canvas = Image.new("RGB", (128, 32), (0, 0, 0))
            canvas_arr = np.array(canvas)

            for px, py, color in pixels:
                angle = random.random() * 2 * math.pi
                distance = progress * 50

                new_x = int(px + math.cos(angle) * distance)
                new_y = int(py + math.sin(angle) * distance)

                if 0 <= new_x < 128 and 0 <= new_y < 32:
                    canvas_arr[new_y, new_x] = color

            frames.append(Image.fromarray(canvas_arr))

        return frames

    @staticmethod
    def matrix_rain(
        text: str, font: Any, duration: float = 3.0, fps: int = 10
    ) -> List[Image.Image]:
        frames: List[Image.Image] = []
        num_frames = int(fps * duration)

        columns = []
        for x in range(0, 128, 8):
            columns.append(
                {
                    "x": x,
                    "y": random.randint(-32, 0),
                    "speed": random.randint(1, 3),
                    "chars": [random.choice(text) for _ in range(10)],
                }
            )

        for _ in range(num_frames):
            canvas = Image.new("RGB", (128, 32), (0, 0, 0))
            draw = ImageDraw.Draw(canvas)

            for col in columns:
                for j, char in enumerate(col["chars"]):
                    y = col["y"] + j * 8
                    if 0 <= y < 32:
                        alpha = 255 - j * 25
                        color = (0, max(0, alpha), 0)
                        draw.text((col["x"], y), char, fill=color, font=font)

                col["y"] += col["speed"]
                if col["y"] > 32:
                    col["y"] = -32

            frames.append(canvas)

        return frames

    @staticmethod
    def spiral_text(
        text_img: Image.Image, duration: float = 3.0, fps: int = 10
    ) -> List[Image.Image]:
        frames: List[Image.Image] = []
        num_frames = int(fps * duration)
        w, h = text_img.size

        for i in range(num_frames):
            progress = i / num_frames
            angle = progress * 360 * 2
            scale = 0.3 + progress * 0.7

            rotated = text_img.rotate(angle, expand=True, fillcolor=(0, 0, 0))
            w2, h2 = rotated.size
            new_w, new_h = int(w2 * scale), int(h2 * scale)
            scaled = rotated.resize((new_w, new_h), Image.Resampling.LANCZOS)

            canvas = Image.new("RGB", (128, 32), (0, 0, 0))
            canvas.paste(scaled, ((128 - new_w) // 2, (32 - new_h) // 2))
            frames.append(canvas)

        return frames

    @staticmethod
    def shake_text(
        text_img: Image.Image, duration: float = 1.0, fps: int = 10, intensity: int = 5
    ) -> List[Image.Image]:
        frames: List[Image.Image] = []
        num_frames = int(fps * duration)

        for _ in range(num_frames):
            x_offset = random.randint(-intensity, intensity)
            y_offset = random.randint(-intensity, intensity)

            canvas = Image.new("RGB", (128, 32), (0, 0, 0))
            canvas.paste(text_img, (x_offset, y_offset))
            frames.append(canvas)

        return frames

    @staticmethod
    def glitch_text(
        text_img: Image.Image, duration: float = 2.0, fps: int = 10
    ) -> List[Image.Image]:
        frames: List[Image.Image] = []
        num_frames = int(fps * duration)
        arr = np.array(text_img)

        for _ in range(num_frames):
            if random.random() < 0.3:
                glitched = arr.copy()

                shift = random.randint(5, 15)
                glitched[:, :, 0] = np.roll(glitched[:, :, 0], shift, axis=1)
                glitched[:, :, 2] = np.roll(glitched[:, :, 2], -shift, axis=1)

                for _ in range(3):
                    y = random.randint(0, 31)
                    glitched[y, :] = random.randint(0, 255)

                frame = Image.fromarray(glitched)
            else:
                frame = text_img.copy()

            canvas = Image.new("RGB", (128, 32), (0, 0, 0))
            canvas.paste(frame, (0, 0))
            frames.append(canvas)

        return frames
