#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DMD GIF Converter 128x32 - IA Enhanced v2.0
Shan_ayA 2026

Application complète de conversion d'images en GIF optimisés pour écrans DMD 128x32
avec intelligence artificielle, édition manuelle avancée et génération de texte animé.

Dépendances:
    pip install pillow numpy
"""

import os
import sys
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageOps, ImageChops, ImageFont, ImageTk, ImageTk
import re
import tkinter as tk
from tkinter import filedialog, ttk, messagebox, colorchooser, font as tkfont
from tkinter import Canvas, Text, Scrollbar
import threading
import numpy as np
from collections import Counter
import time
import datetime
import math
import random

# ============================================================================
# LOGGER
# ============================================================================

class Logger:
    """Système de logging avec callbacks pour affichage temps réel"""
    
    def __init__(self):
        self.logs = []
        self.callbacks = []
    
    def log(self, level, message):
        """Enregistre un log avec timestamp"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_entry = {'time': timestamp, 'level': level, 'message': message}
        self.logs.append(log_entry)
        
        # Notifier tous les callbacks
        for callback in self.callbacks:
            callback(log_entry)
    
    def info(self, msg):
        self.log('INFO', msg)
    
    def warning(self, msg):
        self.log('WARNING', msg)
    
    def error(self, msg):
        self.log('ERROR', msg)
    
    def debug(self, msg):
        self.log('DEBUG', msg)

# Instance globale du logger
logger = Logger()


# ============================================================================
# MOTEUR DMD - Optimisation avancée pour écrans 128x32
# ============================================================================

class DMDEngine:
    """Moteur de rendu optimisé pour écrans DMD avec algorithmes adaptatifs"""
    
    @staticmethod
    def detect_background_color(img):
        """
        Détecte la couleur de fond en analysant les coins de l'image
        Retourne: (couleur_rgb, est_sombre)
        """
        arr = np.array(img.convert('RGB'))
        h, w = arr.shape[:2]
        
        # Analyser coins (10px ou 1/8 de la dimension)
        corner_size = min(10, min(h, w) // 8)
        corners = np.concatenate([
            arr[:corner_size, :corner_size].reshape(-1, 3),
            arr[:corner_size, -corner_size:].reshape(-1, 3),
            arr[-corner_size:, :corner_size].reshape(-1, 3),
            arr[-corner_size:, -corner_size:].reshape(-1, 3)
        ])
        
        bg_candidate = np.median(corners, axis=0).astype(int)
        
        # Forcer noir si très sombre
        if np.mean(bg_candidate) < 40:
            return (0, 0, 0), True
        
        # Forcer noir si proche du noir
        dist_to_black = np.sqrt(np.sum(bg_candidate ** 2))
        if dist_to_black < 80:
            return (0, 0, 0), True
        
        return tuple(bg_candidate), False
    
    @staticmethod
    def detect_palette(img, max_colors=16):
        """
        Détecte les couleurs dominantes de l'image
        Retourne: liste de couleurs RGB triées par fréquence
        """
        # Réduire taille pour performance
        img_small = img.resize((128, 128), Image.Resampling.LANCZOS)
        arr = np.array(img_small.convert('RGB'))
        pixels = arr.reshape(-1, 3)
        
        # Quantification grossière
        quantized = (pixels // 32) * 32
        
        # Compter occurrences
        unique, counts = np.unique(quantized, axis=0, return_counts=True)
        
        # Trier par fréquence
        sorted_indices = np.argsort(-counts)
        palette = [tuple(unique[i]) for i in sorted_indices[:max_colors]]
        
        return palette
    
    @staticmethod
    def optimize_for_dmd(img, settings):
        """
        Optimise l'image pour affichage DMD avec algorithme multi-passes
        - Amélioration contraste adaptatif
        - Réduction bruit
        - Accentuation détails
        """
        img = img.convert('RGB')
        
        # Passe 1: Ajustements de base
        if 'brightness' in settings and settings['brightness'] != 1.0:
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(settings['brightness'])
        
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(settings['contrast'])
        
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(settings['saturation'])
        
        # Passe 2: Accentuation (améliore netteté pour petits écrans)
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.2)
        
        # Passe 3: Optimisation pixels sombres
        arr = np.array(img)
        black_threshold = settings.get('black_threshold', 30)
        mask = np.all(arr < black_threshold, axis=2)
        arr[mask] = [0, 0, 0]
        
        # Passe 4: Réduction bruit sur zones uniformes
        img = Image.fromarray(arr)
        img = img.filter(ImageFilter.MedianFilter(size=3))
        
        return img
    
    @staticmethod
    def adaptive_resize(img, target_w=128, target_h=32, mode='auto'):
        """
        Redimensionnement adaptatif avec préservation qualité
        Modes: 'fit', 'fill', 'auto'
        """
        w, h = img.size
        
        if mode == 'auto':
            ratio = w / h
            target_ratio = target_w / target_h
            mode = 'fit' if abs(ratio - target_ratio) < 0.5 else 'fill'
        
        # Calcul échelle
        if mode == 'fit':
            scale = min(target_w / w, target_h / h)
        else:  # fill
            scale = max(target_w / w, target_h / h)
        
        new_w = int(w * scale)
        new_h = int(h * scale)
        
        # Redimensionnement haute qualité
        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        return img, new_w, new_h
    
    @staticmethod
    def create_animation_frames(img, settings, bg_color=(0, 0, 0)):
        """
        Génère les frames d'animation selon direction et paramètres
        Retourne: (frames, direction_effective)
        """
        w, h = img.size
        direction = settings['direction']
        fps = settings['fps']
        scroll_speed = settings['scroll_speed']
        duration = settings.get('duration', 2.0)
        
        # Auto-détection direction
        if direction == 'auto':
            if w > 128 and h <= 32:
                direction = 'horizontal'
            elif h > 32 and w <= 128:
                direction = 'vertical'
            elif w > 128 and h > 32:
                direction = 'horizontal' if (w - 128) > (h - 32) else 'vertical'
            else:
                direction = 'static'
        
        frames = []
        
        if direction == 'static' or (w <= 128 and h <= 32):
            # Image statique centrée
            canvas = Image.new('RGB', (128, 32), bg_color)
            x = (128 - w) // 2
            y = (32 - h) // 2
            canvas.paste(img, (x, y))
            num_frames = max(int(fps * duration), 1)
            frames = [canvas] * num_frames
            
        elif direction == 'horizontal':
            # Scroll horizontal (aller-retour)
            max_offset = max(0, w - 128)
            y = (32 - h) // 2
            
            # Aller
            for offset in range(0, max_offset + 1, scroll_speed):
                canvas = Image.new('RGB', (128, 32), bg_color)
                canvas.paste(img, (-offset, y))
                frames.append(canvas)
            
            # Retour
            for offset in range(max_offset, -1, -scroll_speed):
                canvas = Image.new('RGB', (128, 32), bg_color)
                canvas.paste(img, (-offset, y))
                frames.append(canvas)
                
        elif direction == 'vertical':
            # Scroll vertical (aller-retour)
            max_offset = max(0, h - 32)
            x = (128 - w) // 2
            
            # Aller
            for offset in range(0, max_offset + 1, scroll_speed):
                canvas = Image.new('RGB', (128, 32), bg_color)
                canvas.paste(img, (x, -offset))
                frames.append(canvas)
            
            # Retour
            for offset in range(max_offset, -1, -scroll_speed):
                canvas = Image.new('RGB', (128, 32), bg_color)
                canvas.paste(img, (x, -offset))
                frames.append(canvas)
        
        # Assurer durée minimale
        if frames and len(frames) < fps * duration:
            multiplier = int((fps * duration) / len(frames)) + 1
            frames = frames * multiplier
        
        return frames if frames else [Image.new('RGB', (128, 32), bg_color)], direction


# ============================================================================
# EFFETS MANUELS AVANCÉS
# ============================================================================

class ManualEffects:
    """Collection d'effets avancés pour l'édition manuelle"""
    
    @staticmethod
    def scroll_effect(img, direction='horizontal', speed=2, duration=2.0, fps=10):
        """Scroll classique"""
        return DMDEngine.create_animation_frames(
            img, 
            {'direction': direction, 'scroll_speed': speed, 'duration': duration, 'fps': fps},
            (0, 0, 0)
        )[0]
    
    @staticmethod
    def fade_effect(img, duration=2.0, fps=10, fade_in=True):
        """Fade in/out"""
        frames = []
        num_frames = int(fps * duration)
        
        for i in range(num_frames):
            alpha = i / num_frames if fade_in else 1 - (i / num_frames)
            frame = img.copy()
            
            # Simuler alpha en assombrissant
            enhancer = ImageEnhance.Brightness(frame)
            frame = enhancer.enhance(alpha)
            
            canvas = Image.new('RGB', (128, 32), (0, 0, 0))
            w, h = frame.size
            x, y = (128 - w) // 2, (32 - h) // 2
            canvas.paste(frame, (x, y))
            frames.append(canvas)
        
        return frames
    
    @staticmethod
    def zoom_effect(img, duration=2.0, fps=10, zoom_in=True):
        """Zoom in/out"""
        frames = []
        num_frames = int(fps * duration)
        
        for i in range(num_frames):
            progress = i / num_frames
            scale = 0.5 + progress * 0.5 if zoom_in else 1.0 - progress * 0.5
            
            w, h = img.size
            new_w, new_h = int(w * scale), int(h * scale)
            scaled = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            
            canvas = Image.new('RGB', (128, 32), (0, 0, 0))
            x, y = (128 - new_w) // 2, (32 - new_h) // 2
            canvas.paste(scaled, (x, y))
            frames.append(canvas)
        
        return frames
    
    @staticmethod
    def rotate_effect(img, duration=2.0, fps=10):
        """Rotation 360°"""
        frames = []
        num_frames = int(fps * duration)
        
        for i in range(num_frames):
            angle = (i / num_frames) * 360
            rotated = img.rotate(angle, expand=True, fillcolor=(0, 0, 0))
            
            canvas = Image.new('RGB', (128, 32), (0, 0, 0))
            w, h = rotated.size
            x, y = (128 - w) // 2, (32 - h) // 2
            canvas.paste(rotated, (x, y))
            frames.append(canvas)
        
        return frames
    
    @staticmethod
    def wave_effect(img, duration=2.0, fps=10, amplitude=5):
        """Effet vague"""
        frames = []
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
            canvas = Image.new('RGB', (128, 32), (0, 0, 0))
            canvas.paste(frame, ((128 - w) // 2, (32 - h) // 2))
            frames.append(canvas)
        
        return frames
    
    @staticmethod
    def bounce_effect(img, duration=2.0, fps=10):
        """Rebond"""
        frames = []
        num_frames = int(fps * duration)
        
        for i in range(num_frames):
            progress = i / num_frames
            # Fonction rebond (sin²)
            y_offset = int(abs(math.sin(progress * math.pi * 2)) * 10)
            
            canvas = Image.new('RGB', (128, 32), (0, 0, 0))
            w, h = img.size
            x = (128 - w) // 2
            y = (32 - h) // 2 - y_offset
            canvas.paste(img, (x, y))
            frames.append(canvas)
        
        return frames
    
    @staticmethod
    def flash_effect(img, duration=1.0, fps=10, flashes=3):
        """Flash stroboscopique"""
        frames = []
        num_frames = int(fps * duration)
        flash_interval = num_frames // (flashes * 2)
        
        for i in range(num_frames):
            is_flash = (i // flash_interval) % 2 == 0
            
            canvas = Image.new('RGB', (128, 32), (255, 255, 255) if is_flash else (0, 0, 0))
            if not is_flash:
                w, h = img.size
                canvas.paste(img, ((128 - w) // 2, (32 - h) // 2))
            frames.append(canvas)
        
        return frames
    
    @staticmethod
    def slide_effect(img, direction='left', duration=1.0, fps=10):
        """Slide depuis un côté"""
        frames = []
        num_frames = int(fps * duration)
        w, h = img.size
        
        for i in range(num_frames):
            progress = i / num_frames
            
            canvas = Image.new('RGB', (128, 32), (0, 0, 0))
            
            if direction == 'left':
                x = int(-w + progress * (128 + w)) - 128 // 2
                y = (32 - h) // 2
            elif direction == 'right':
                x = int(128 - progress * (128 + w)) + 128 // 2
                y = (32 - h) // 2
            elif direction == 'top':
                x = (128 - w) // 2
                y = int(-h + progress * (32 + h)) - 32 // 2
            else:  # bottom
                x = (128 - w) // 2
                y = int(32 - progress * (32 + h)) + 32 // 2
            
            canvas.paste(img, (x, y))
            frames.append(canvas)
        
        return frames
    
    @staticmethod
    def spiral_effect(img, duration=2.0, fps=10):
        """Spirale"""
        frames = []
        num_frames = int(fps * duration)
        
        for i in range(num_frames):
            progress = i / num_frames
            angle = progress * 360 * 2
            scale = 0.3 + progress * 0.7
            
            w, h = img.size
            new_w, new_h = int(w * scale), int(h * scale)
            scaled = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            rotated = scaled.rotate(angle, expand=True, fillcolor=(0, 0, 0))
            
            canvas = Image.new('RGB', (128, 32), (0, 0, 0))
            rw, rh = rotated.size
            canvas.paste(rotated, ((128 - rw) // 2, (32 - rh) // 2))
            frames.append(canvas)
        
        return frames
    
    @staticmethod
    def shake_effect(img, duration=1.0, fps=10, intensity=5):
        """Tremblement"""
        frames = []
        num_frames = int(fps * duration)
        
        for i in range(num_frames):
            x_offset = random.randint(-intensity, intensity)
            y_offset = random.randint(-intensity, intensity)
            
            canvas = Image.new('RGB', (128, 32), (0, 0, 0))
            w, h = img.size
            x = (128 - w) // 2 + x_offset
            y = (32 - h) // 2 + y_offset
            canvas.paste(img, (x, y))
            frames.append(canvas)
        
        return frames
    
    @staticmethod
    def pulse_effect(img, duration=2.0, fps=10):
        """Pulsation"""
        frames = []
        num_frames = int(fps * duration)
        
        for i in range(num_frames):
            progress = i / num_frames
            scale = 0.8 + 0.4 * abs(math.sin(progress * math.pi * 2))
            
            w, h = img.size
            new_w, new_h = int(w * scale), int(h * scale)
            scaled = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            
            canvas = Image.new('RGB', (128, 32), (0, 0, 0))
            canvas.paste(scaled, ((128 - new_w) // 2, (32 - new_h) // 2))
            frames.append(canvas)
        
        return frames
    
    @staticmethod
    def glitch_effect(img, duration=1.0, fps=10):
        """Effet glitch"""
        frames = []
        num_frames = int(fps * duration)
        arr = np.array(img)
        
        for i in range(num_frames):
            if random.random() < 0.3:  # 30% chance de glitch
                glitched = arr.copy()
                
                # Décalage RGB
                shift = random.randint(5, 15)
                glitched[:, :, 0] = np.roll(glitched[:, :, 0], shift, axis=1)
                glitched[:, :, 2] = np.roll(glitched[:, :, 2], -shift, axis=1)
                
                frame = Image.fromarray(glitched)
            else:
                frame = img.copy()
            
            canvas = Image.new('RGB', (128, 32), (0, 0, 0))
            w, h = frame.size
            canvas.paste(frame, ((128 - w) // 2, (32 - h) // 2))
            frames.append(canvas)
        
        return frames
    
    @staticmethod
    def pixelate_effect(img, duration=2.0, fps=10):
        """Pixelisation progressive"""
        frames = []
        num_frames = int(fps * duration)
        
        for i in range(num_frames):
            progress = i / num_frames
            pixel_size = int(1 + progress * 10)
            
            w, h = img.size
            small = img.resize((w // pixel_size, h // pixel_size), Image.Resampling.NEAREST)
            pixelated = small.resize((w, h), Image.Resampling.NEAREST)
            
            canvas = Image.new('RGB', (128, 32), (0, 0, 0))
            canvas.paste(pixelated, ((128 - w) // 2, (32 - h) // 2))
            frames.append(canvas)
        
        return frames
    
    @staticmethod
    def blur_transition_effect(img, duration=2.0, fps=10):
        """Transition floue"""
        frames = []
        num_frames = int(fps * duration)
        
        for i in range(num_frames):
            progress = i / num_frames
            radius = int(progress * 10)
            
            if radius > 0:
                blurred = img.filter(ImageFilter.GaussianBlur(radius=radius))
            else:
                blurred = img.copy()
            
            canvas = Image.new('RGB', (128, 32), (0, 0, 0))
            w, h = blurred.size
            canvas.paste(blurred, ((128 - w) // 2, (32 - h) // 2))
            frames.append(canvas)
        
        return frames
    
    @staticmethod
    def color_shift_effect(img, duration=2.0, fps=10):
        """Décalage de couleurs"""
        frames = []
        num_frames = int(fps * duration)
        arr = np.array(img)
        
        for i in range(num_frames):
            progress = i / num_frames
            angle = progress * 360
            
            # Rotation teinte HSV
            shifted = arr.copy()
            hsv = Image.fromarray(shifted).convert('HSV')
            h, s, v = hsv.split()
            h_arr = np.array(h)
            h_arr = (h_arr + int(angle)) % 256
            h = Image.fromarray(h_arr.astype('uint8'))
            shifted_img = Image.merge('HSV', (h, s, v)).convert('RGB')
            
            canvas = Image.new('RGB', (128, 32), (0, 0, 0))
            w, h = shifted_img.size
            canvas.paste(shifted_img, ((128 - w) // 2, (32 - h) // 2))
            frames.append(canvas)
        
        return frames


# ============================================================================
# EFFETS TEXTE AVANCÉS
# ============================================================================

class TextEffects:
    """Effets visuels avancés pour texte"""
    
    @staticmethod
    def effect_3d(draw, text, pos, font, color, bg_color):
        """Effet 3D avec ombre décalée"""
        x, y = pos
        depth = 3
        
        # Ombres progressives
        for i in range(depth, 0, -1):
            shadow_color = tuple(max(0, c - i * 30) for c in color)
            draw.text((x + i, y + i), text, fill=shadow_color, font=font)
        
        # Texte principal
        draw.text(pos, text, fill=color, font=font)
    
    @staticmethod
    def effect_fire(draw, text, pos, font, base_color=(255, 100, 0)):
        """Effet flamme avec dégradé"""
        x, y = pos
        
        # Dégradé vertical
        bbox = draw.textbbox(pos, text, font=font)
        height = bbox[3] - bbox[1]
        
        for offset in range(height):
            progress = offset / height
            r = int(255 * (1 - progress * 0.3))
            g = int(100 + 155 * progress)
            b = int(progress * 50)
            color = (r, g, b)
            
            draw.text((x, y + offset), text, fill=color, font=font)
    
    @staticmethod
    def effect_snow(img, text_img):
        """Effet neige tombante"""
        arr = np.array(text_img)
        h, w = arr.shape[:2]
        
        # Ajouter flocons
        for _ in range(50):
            x = random.randint(0, w - 1)
            y = random.randint(0, h - 1)
            arr[y, x] = [255, 255, 255]
        
        return Image.fromarray(arr)
    
    @staticmethod
    def effect_ice(draw, text, pos, font):
        """Effet glace cristalline"""
        x, y = pos
        
        # Contour bleu clair
        for dx in [-2, -1, 0, 1, 2]:
            for dy in [-2, -1, 0, 1, 2]:
                if dx != 0 or dy != 0:
                    draw.text((x + dx, y + dy), text, fill=(100, 150, 255), font=font)
        
        # Texte blanc glacé
        draw.text(pos, text, fill=(200, 230, 255), font=font)
    
    @staticmethod
    def effect_metal(draw, text, pos, font):
        """Effet métal chromé"""
        x, y = pos
        
        # Dégradé métallique
        bbox = draw.textbbox(pos, text, font=font)
        width = bbox[2] - bbox[0]
        
        for offset in range(width):
            progress = offset / width
            gray = int(100 + 100 * abs(math.sin(progress * math.pi * 2)))
            color = (gray, gray, gray + 50)
            
            # Dessiner ligne verticale
            draw.line([(x + offset, y), (x + offset, y + 30)], fill=color, width=1)
        
        # Texte par-dessus
        draw.text(pos, text, fill=(220, 220, 255), font=font)
    
    @staticmethod
    def effect_neon(draw, text, pos, font, color=(0, 255, 255)):
        """Effet néon lumineux"""
        x, y = pos
        
        # Halo externe
        for radius in range(5, 0, -1):
            alpha = 50 + radius * 20
            glow_color = tuple(min(255, c + alpha) for c in color)
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    if dx * dx + dy * dy <= radius * radius:
                        draw.text((x + dx, y + dy), text, fill=glow_color, font=font)
        
        # Texte principal
        draw.text(pos, text, fill=(255, 255, 255), font=font)
    
    @staticmethod
    def effect_graffiti(draw, text, pos, font, colors=None):
        """Effet graffiti multi-couleurs"""
        if colors is None:
            colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
        
        x, y = pos
        
        # Contour noir épais
        for dx in range(-3, 4):
            for dy in range(-3, 4):
                if dx != 0 or dy != 0:
                    draw.text((x + dx, y + dy), text, fill=(0, 0, 0), font=font)
        
        # Texte avec couleur aléatoire par lettre
        for i, char in enumerate(text):
            color = colors[i % len(colors)]
            char_x = x + i * 10  # Approximation
            draw.text((char_x, y), char, fill=color, font=font)
    
    @staticmethod
    def effect_pixel_art(img):
        """Effet pixel art rétro"""
        w, h = img.size
        pixelated = img.resize((w // 4, h // 4), Image.Resampling.NEAREST)
        return pixelated.resize((w, h), Image.Resampling.NEAREST)
    
    @staticmethod
    def effect_rainbow(draw, text, pos, font):
        """Effet arc-en-ciel"""
        x, y = pos
        colors = [
            (255, 0, 0), (255, 127, 0), (255, 255, 0),
            (0, 255, 0), (0, 0, 255), (75, 0, 130), (148, 0, 211)
        ]
        
        # Dessiner chaque lettre avec couleur différente
        offset_x = 0
        for i, char in enumerate(text):
            color = colors[i % len(colors)]
            draw.text((x + offset_x, y), char, fill=color, font=font)
            bbox = draw.textbbox((x + offset_x, y), char, font=font)
            offset_x += bbox[2] - bbox[0]
    
    @staticmethod
    def effect_matrix(draw, text, pos, font):
        """Effet Matrix (vert sur noir)"""
        x, y = pos
        
        # Traînées vertes
        for offset in range(5):
            alpha = 255 - offset * 50
            green = max(0, alpha)
            draw.text((x, y - offset * 2), text, fill=(0, green, 0), font=font)
        
        # Texte principal vert vif
        draw.text(pos, text, fill=(0, 255, 0), font=font)
    
    @staticmethod
    def effect_gradient(draw, text, pos, font, color1, color2):
        """Dégradé de couleur"""
        x, y = pos
        bbox = draw.textbbox(pos, text, font=font)
        width = bbox[2] - bbox[0]
        
        for offset in range(width):
            progress = offset / width
            r = int(color1[0] + (color2[0] - color1[0]) * progress)
            g = int(color1[1] + (color2[1] - color1[1]) * progress)
            b = int(color1[2] + (color2[2] - color1[2]) * progress)
            
            # Dessiner ligne verticale
            draw.line([(x + offset, y), (x + offset, y + 30)], fill=(r, g, b), width=1)


# ============================================================================
# ANIMATIONS TEXTE AVANCÉES
# ============================================================================

class TextAnimations:
    """Animations avancées pour texte défilant"""
    
    @staticmethod
    def scroll_wave(text_img, duration=3.0, fps=10):
        """Scroll avec effet vague"""
        frames = []
        num_frames = int(fps * duration)
        w, h = text_img.size
        
        for i in range(num_frames):
            progress = i / num_frames
            offset_x = int(progress * (w + 128))
            
            canvas = Image.new('RGB', (128, 32), (0, 0, 0))
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
    def starwars_scroll(text_img, duration=5.0, fps=10):
        """Scroll style Star Wars (perspective)"""
        frames = []
        num_frames = int(fps * duration)
        w, h = text_img.size
        
        for i in range(num_frames):
            progress = i / num_frames
            
            canvas = Image.new('RGB', (128, 32), (0, 0, 0))
            
            # Perspective: rétrécir en haut
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
    def bounce_scroll(text_img, duration=3.0, fps=10):
        """Scroll avec rebonds"""
        frames = []
        num_frames = int(fps * duration)
        w, h = text_img.size
        
        for i in range(num_frames):
            progress = i / num_frames
            offset_x = int(progress * (w + 128))
            bounce_y = int(abs(math.sin(progress * math.pi * 4)) * 10)
            
            canvas = Image.new('RGB', (128, 32), (0, 0, 0))
            
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
    def typewriter(text, font, color, bg_color, duration=3.0, fps=10):
        """Effet machine à écrire"""
        frames = []
        num_frames = int(fps * duration)
        chars_per_frame = max(1, len(text) // num_frames)
        
        for i in range(num_frames):
            visible_text = text[:i * chars_per_frame]
            
            img = Image.new('RGB', (500, 32), bg_color)
            draw = ImageDraw.Draw(img)
            draw.text((10, 8), visible_text, fill=color, font=font)
            
            # Centrer sur canvas
            canvas = Image.new('RGB', (128, 32), bg_color)
            canvas.paste(img.crop((0, 0, 128, 32)), (0, 0))
            frames.append(canvas)
        
        return frames
    
    @staticmethod
    def explode(text_img, duration=2.0, fps=10):
        """Explosion de texte"""
        frames = []
        num_frames = int(fps * duration)
        w, h = text_img.size
        arr = np.array(text_img)
        
        # Détecter pixels non-noirs
        pixels = []
        for y in range(h):
            for x in range(w):
                if np.any(arr[y, x] > 10):
                    pixels.append((x, y, arr[y, x]))
        
        for i in range(num_frames):
            progress = i / num_frames
            canvas = Image.new('RGB', (128, 32), (0, 0, 0))
            canvas_arr = np.array(canvas)
            
            for px, py, color in pixels:
                # Trajectoire aléatoire
                angle = random.random() * 2 * math.pi
                distance = progress * 50
                
                new_x = int(px + math.cos(angle) * distance)
                new_y = int(py + math.sin(angle) * distance)
                
                if 0 <= new_x < 128 and 0 <= new_y < 32:
                    canvas_arr[new_y, new_x] = color
            
            frames.append(Image.fromarray(canvas_arr))
        
        return frames
    
    @staticmethod
    def matrix_rain(text, font, duration=3.0, fps=10):
        """Pluie Matrix"""
        frames = []
        num_frames = int(fps * duration)
        
        # Colonnes de caractères
        columns = []
        for x in range(0, 128, 8):
            columns.append({
                'x': x,
                'y': random.randint(-32, 0),
                'speed': random.randint(1, 3),
                'chars': [random.choice(text) for _ in range(10)]
            })
        
        for i in range(num_frames):
            canvas = Image.new('RGB', (128, 32), (0, 0, 0))
            draw = ImageDraw.Draw(canvas)
            
            for col in columns:
                for j, char in enumerate(col['chars']):
                    y = col['y'] + j * 8
                    if 0 <= y < 32:
                        alpha = 255 - j * 25
                        color = (0, max(0, alpha), 0)
                        draw.text((col['x'], y), char, fill=color, font=font)
                
                col['y'] += col['speed']
                if col['y'] > 32:
                    col['y'] = -32
            
            frames.append(canvas)
        
        return frames
    
    @staticmethod
    def spiral_text(text_img, duration=3.0, fps=10):
        """Spirale de texte"""
        frames = []
        num_frames = int(fps * duration)
        
        for i in range(num_frames):
            progress = i / num_frames
            angle = progress * 360 * 2
            scale = 0.3 + progress * 0.7
            
            rotated = text_img.rotate(angle, expand=True, fillcolor=(0, 0, 0))
            w, h = rotated.size
            new_w, new_h = int(w * scale), int(h * scale)
            scaled = rotated.resize((new_w, new_h), Image.Resampling.LANCZOS)
            
            canvas = Image.new('RGB', (128, 32), (0, 0, 0))
            canvas.paste(scaled, ((128 - new_w) // 2, (32 - new_h) // 2))
            frames.append(canvas)
        
        return frames
    
    @staticmethod
    def shake_text(text_img, duration=1.0, fps=10, intensity=5):
        """Texte tremblant"""
        frames = []
        num_frames = int(fps * duration)
        
        for i in range(num_frames):
            x_offset = random.randint(-intensity, intensity)
            y_offset = random.randint(-intensity, intensity)
            
            canvas = Image.new('RGB', (128, 32), (0, 0, 0))
            canvas.paste(text_img, (x_offset, y_offset))
            frames.append(canvas)
        
        return frames
    
    @staticmethod
    def glitch_text(text_img, duration=2.0, fps=10):
        """Glitch numérique"""
        frames = []
        num_frames = int(fps * duration)
        arr = np.array(text_img)
        
        for i in range(num_frames):
            if random.random() < 0.3:
                glitched = arr.copy()
                
                # Décalage RGB
                shift = random.randint(5, 15)
                glitched[:, :, 0] = np.roll(glitched[:, :, 0], shift, axis=1)
                glitched[:, :, 2] = np.roll(glitched[:, :, 2], -shift, axis=1)
                
                # Lignes corrompues
                for _ in range(3):
                    y = random.randint(0, 31)
                    glitched[y, :] = random.randint(0, 255)
                
                frame = Image.fromarray(glitched)
            else:
                frame = text_img.copy()
            
            canvas = Image.new('RGB', (128, 32), (0, 0, 0))
            canvas.paste(frame, (0, 0))
            frames.append(canvas)
        
        return frames


# ============================================================================
# APPLICATION PRINCIPALE
# ============================================================================

class DMDConverter:
    """Application principale de conversion DMD"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("DMD GIF Converter 128x32 - IA Enhanced v2.0")
        self.root.state('zoomed')  # Plein écran fenêtré
        
        # Données
        self.images = []
        self.current_preview = None
        self.preview_frames = []
        self.preview_index = 0
        self.animating = False
        self.current_image_idx = None
        self.current_fps = 10
        
        self.image_settings = {}
        self.manual_exports = set()
        self.proposals = []
        self.selected_proposal = 0
        self.locked_proposal = None
        
        # Paramètres
        self.theme = tk.StringVar(value="dark")
        self.add_anim_to_name = tk.BooleanVar(value=True)
        
        # Manuel
        self.manual_image = None
        self.manual_original = None
        self.manual_history = []
        self.fill_mode = False
        self.fill_color = (255, 0, 0)
        self.manual_frames = []
        self.manual_animating = False
        self.manual_frame_idx = 0
        self.eraser_mode = False
        self.eraser_tolerance = 30
        # Crop mode
        self.crop_mode = False
        self.crop_start = None
        self.crop_rect = None
        self.crop_preview_rect = None
        
        # Text scroll
        self.text_frames = []
        # Polices système Windows détectées
        self.windows_fonts = ['Agency FB', 'Algerian', 'AniMe Vision - MB_EN', 'Arabic Transparent', 'Arial', 'Arial Baltic', 'Arial Black', 'Arial CE', 'Arial CYR', 'Arial Greek', 'Arial Narrow', 'Arial Rounded MT Bold', 'Arial TUR', 'BadaBoom BB', 'Bahnschrift', 'Bahnschrift Condensed', 'Bahnschrift Light', 'Bahnschrift Light Condensed', 'Bahnschrift Light SemiCondensed', 'Bahnschrift SemiBold', 'Bahnschrift SemiBold Condensed', 'Bahnschrift SemiBold SemiConden', 'Bahnschrift SemiCondensed', 'Bahnschrift SemiLight', 'Bahnschrift SemiLight Condensed', 'Bahnschrift SemiLight SemiConde', 'Baskerville Old Face', 'Bauhaus 93', 'Bell MT', 'Berlin Sans FB', 'Berlin Sans FB Demi', 'Bernard MT Condensed', 'Blackadder ITC', 'Bodoni MT', 'Bodoni MT Black', 'Bodoni MT Condensed', 'Bodoni MT Poster Compressed', 'Book Antiqua', 'Bookman Old Style', 'Bookshelf Symbol 7', 'Bradley Hand ITC', 'Britannic Bold', 'Broadway', 'Brush Script MT', 'Calibri', 'Calibri Light', 'Californian FB', 'Calisto MT', 'Cambria', 'Cambria Math', 'Candara', 'Candara Light', 'Cascadia Code', 'Cascadia Code ExtraLight', 'Cascadia Code Light', 'Cascadia Code SemiBold', 'Cascadia Code SemiLight', 'Cascadia Mono', 'Cascadia Mono ExtraLight', 'Cascadia Mono Light', 'Cascadia Mono SemiBold', 'Cascadia Mono SemiLight', 'Castellar', 'Centaur', 'Century', 'Century Gothic', 'Century Schoolbook', 'Chiller', 'Colonna MT', 'Comic Sans MS', 'Consolas', 'Constantia', 'Cooper Black', 'Copperplate Gothic Bold', 'Copperplate Gothic Light', 'Corbel', 'Corbel Light', 'Courier', 'Courier New', 'Courier New Baltic', 'Courier New CE', 'Courier New CYR', 'Courier New Greek', 'Courier New TUR', 'Curlz MT', 'DIN Alternate', 'DIN Condensed', 'Dubai', 'Dubai Light', 'Dubai Medium', 'Ebrima', 'Edwardian Script ITC', 'Elephant', 'Engravers MT', 'Eras Bold ITC', 'Eras Demi ITC', 'Eras Light ITC', 'Eras Medium ITC', 'Felix Titling', 'Fixedsys', 'Footlight MT Light', 'Forte', 'Franklin Gothic Book', 'Franklin Gothic Demi', 'Franklin Gothic Demi Cond', 'Franklin Gothic Heavy', 'Franklin Gothic Medium', 'Franklin Gothic Medium Cond', 'Freestyle Script', 'French Script MT', 'Gabriola', 'Gadugi', 'Garamond', 'Georgia', 'Gigi', 'Gill Sans MT', 'Gill Sans MT Condensed', 'Gill Sans MT Ext Condensed Bold', 'Gill Sans Ultra Bold', 'Gill Sans Ultra Bold Condensed', 'Gloucester MT Extra Condensed', 'Goudy Old Style', 'Goudy Stout', 'Haettenschweiler', 'Harlow Solid Italic', 'HarmonyOS Sans SC', 'Harrington', 'High Tower Text', 'Impact', 'Imprint MT Shadow', 'Informal Roman', 'Ink Free', 'Javanese Text', 'Jokerman', 'Juice ITC', 'Karmatic Arcade', 'Kristen ITC', 'Kunstler Script', 'Lato', 'Lato Light', 'Lato Semibold', 'Leelawadee UI', 'Leelawadee UI Semilight', 'Lucida Bright', 'Lucida Calligraphy', 'Lucida Console', 'Lucida Fax', 'Lucida Handwriting', 'Lucida Sans', 'Lucida Sans Typewriter', 'Lucida Sans Unicode', 'MS Gothic', 'MS Outlook', 'MS PGothic', 'MS Reference Sans Serif', 'MS Reference Specialty', 'MS Sans Serif', 'MS Serif', 'MS UI Gothic', 'MT Extra', 'MV Boli', 'Magneto', 'Maiandra GD', 'Malgun Gothic', 'Malgun Gothic Semilight', 'Marlett', 'Matura MT Script Capitals', 'Microsoft Himalaya', 'Microsoft JhengHei', 'Microsoft JhengHei Light', 'Microsoft JhengHei UI', 'Microsoft JhengHei UI Light', 'Microsoft New Tai Lue', 'Microsoft PhagsPa', 'Microsoft Sans Serif', 'Microsoft Tai Le', 'Microsoft YaHei', 'Microsoft YaHei Light', 'Microsoft YaHei UI', 'Microsoft YaHei UI Light', 'Microsoft Yi Baiti', 'MingLiU-ExtB', 'MingLiU_HKSCS-ExtB', 'MingLiU_MSCS-ExtB', 'Mistral', 'Modern', 'Modern No. 20', 'Mongolian Baiti', 'Monotype Corsiva', 'Myanmar Text', 'NSimSun', 'NanumGothic', 'Niagara Engraved', 'Niagara Solid', 'Nirmala Text', 'Nirmala Text Semilight', 'Nirmala UI', 'Nirmala UI Semilight', 'Noto Sans JP', 'OCR A Extended', 'Old English Text MT', 'Onyx', 'PMingLiU-ExtB', 'Palace Script MT', 'Palatino Linotype', 'Papyrus', 'Parchment', 'Perpetua', 'Perpetua Titling MT', 'Playbill', 'Poor Richard', 'Pristina', 'ROG Fonts', 'ROG Fonts STRIX SCAR', 'ROG Fonts v1.6', 'Rage Italic', 'Ravie', 'Roboto', 'Rockwell', 'Rockwell Condensed', 'Rockwell Extra Bold', 'Roman', 'Sans Serif Collection', 'Script', 'Script MT Bold', 'Segoe Fluent Icons', 'Segoe MDL2 Assets', 'Segoe Print', 'Segoe Script', 'Segoe UI', 'Segoe UI Black', 'Segoe UI Emoji', 'Segoe UI Historic', 'Segoe UI Light', 'Segoe UI Semibold', 'Segoe UI Semilight', 'Segoe UI Symbol', 'Segoe UI Variable Display', 'Segoe UI Variable Display Light', 'Segoe UI Variable Display Semib', 'Segoe UI Variable Display Semil', 'Segoe UI Variable Small', 'Segoe UI Variable Small Light', 'Segoe UI Variable Small Semibol', 'Segoe UI Variable Small Semilig', 'Segoe UI Variable Text', 'Segoe UI Variable Text Light', 'Segoe UI Variable Text Semibold', 'Segoe UI Variable Text Semiligh', 'Shaka Pow', 'Showcard Gothic', 'SimSun', 'SimSun-ExtB', 'SimSun-ExtG', 'Sitka Banner', 'Sitka Banner Semibold', 'Sitka Display', 'Sitka Display Semibold', 'Sitka Heading', 'Sitka Heading Semibold', 'Sitka Small', 'Sitka Small Semibold', 'Sitka Subheading', 'Sitka Subheading Semibold', 'Sitka Text', 'Sitka Text Semibold', 'Small Fonts', 'Snap ITC', 'Source Han Sans JP', 'Source Han Sans JP Normal', 'Stencil', 'Sylfaen', 'Symbol', 'System', 'Tahoma', 'Tempus Sans ITC', 'Terminal', 'Times New Roman', 'Times New Roman Baltic', 'Times New Roman CE', 'Times New Roman CYR', 'Times New Roman Greek', 'Times New Roman TUR', 'Trebuchet MS', 'Tw Cen MT', 'Tw Cen MT Condensed', 'Tw Cen MT Condensed Extra Bold', 'Verdana', 'Viner Hand ITC', 'Vivaldi', 'Vladimir Script', 'Webdings', 'Wide Latin', 'Wingdings', 'Wingdings 2', 'Wingdings 3', 'Xolonium', 'Yu Gothic', 'Yu Gothic Light', 'Yu Gothic Medium', 'Yu Gothic UI', 'Yu Gothic UI Light', 'Yu Gothic UI Semibold', 'Yu Gothic UI Semilight']

        self.text_animating = False
        self.text_frame_idx = 0
        
        self.setup_ui()
        self.apply_theme()
        logger.info("Application démarrée v2.0")
    
    def setup_ui(self):
        """Construction de l'interface utilisateur"""
        # Container principal
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Header avec thème
        header = ttk.Frame(main_container)
        header.pack(fill=tk.X, padx=10, pady=(5, 0))
        
        ttk.Label(header, text="DMD Converter v2.0", font=('Arial', 12, 'bold')).pack(side=tk.LEFT)
        
        # Notebook
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Onglets
        self.auto_frame = ttk.Frame(self.notebook)
        self.manual_frame = ttk.Frame(self.notebook)
        self.textscroll_frame = ttk.Frame(self.notebook)
        self.params_frame = ttk.Frame(self.notebook)
        self.debug_frame = ttk.Frame(self.notebook)
        
        self.notebook.add(self.auto_frame, text="AUTO")
        self.notebook.add(self.manual_frame, text="MANUEL")
        self.notebook.add(self.textscroll_frame, text="TEXTSCROLL")
        self.notebook.add(self.params_frame, text="PARAMETRES")
        self.notebook.add(self.debug_frame, text="DEBUG")
        
        # Bind changement onglet
        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_changed)
        
        self.setup_auto_tab()
        self.setup_manual_tab()
        self.setup_textscroll_tab()
        self.setup_params_tab()
        self.setup_debug_tab()
        
        # Footer
        footer = ttk.Frame(main_container)
        footer.pack(fill=tk.X, padx=10, pady=(0, 5))
        
        self.progress_var = tk.StringVar(value="Prêt")
        ttk.Label(footer, textvariable=self.progress_var).pack(side=tk.LEFT)
        
        ttk.Label(footer, text="Shan_ayA 2026", font=('Arial', 8, 'italic')).pack(side=tk.RIGHT)
    
    def setup_auto_tab(self):
        """Configuration onglet AUTO avec IA"""
        main_frame = ttk.Frame(self.auto_frame, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(header_frame, text="Source:").pack(side=tk.LEFT)
        ttk.Button(header_frame, text="📁 Dossier", command=self.select_folder).pack(side=tk.LEFT, padx=5)
        ttk.Button(header_frame, text="🖼️ Images", command=self.select_images).pack(side=tk.LEFT, padx=5)
        self.recursive_var = tk.BooleanVar()
        ttk.Checkbutton(header_frame, text="Récursif", variable=self.recursive_var).pack(side=tk.LEFT, padx=5)
        
        # Paramètres globaux
        params_frame = ttk.LabelFrame(main_frame, text="Paramètres Globaux", padding="5")
        params_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Ligne 1
        row1 = ttk.Frame(params_frame)
        row1.pack(fill=tk.X, pady=2)
        
        ttk.Label(row1, text="FPS:").pack(side=tk.LEFT)
        self.fps_var = tk.IntVar(value=10)
        ttk.Spinbox(row1, from_=1, to=60, textvariable=self.fps_var, width=10,
                   command=self.on_global_param_change).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(row1, text="Durée (s):").pack(side=tk.LEFT, padx=(20, 5))
        self.duration_var = tk.DoubleVar(value=2.0)
        ttk.Spinbox(row1, from_=0.5, to=10, increment=0.5, textvariable=self.duration_var, width=10,
                   command=self.on_global_param_change).pack(side=tk.LEFT)
        
        ttk.Label(row1, text="Vitesse scroll:").pack(side=tk.LEFT, padx=(20, 5))
        self.scroll_speed_var = tk.IntVar(value=1)
        ttk.Spinbox(row1, from_=1, to=10, textvariable=self.scroll_speed_var, width=10,
                   command=self.on_global_param_change).pack(side=tk.LEFT)
        
        # Ligne 2
        row2 = ttk.Frame(params_frame)
        row2.pack(fill=tk.X, pady=2)
        
        ttk.Label(row2, text="Contraste:").pack(side=tk.LEFT)
        self.contrast_var = tk.DoubleVar(value=1.5)
        ttk.Spinbox(row2, from_=1.0, to=3.0, increment=0.1, textvariable=self.contrast_var, width=10,
                   command=self.on_global_param_change).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(row2, text="Saturation:").pack(side=tk.LEFT, padx=(20, 5))
        self.saturation_var = tk.DoubleVar(value=1.3)
        ttk.Spinbox(row2, from_=0.5, to=2.0, increment=0.1, textvariable=self.saturation_var, width=10,
                   command=self.on_global_param_change).pack(side=tk.LEFT)
        
        ttk.Label(row2, text="Couleurs GIF:").pack(side=tk.LEFT, padx=(20, 5))
        self.color_count_var = tk.IntVar(value=256)
        color_combo = ttk.Combobox(row2, textvariable=self.color_count_var,
                                   values=[8, 16, 32, 64, 128, 256], state="readonly", width=10)
        color_combo.pack(side=tk.LEFT)
        color_combo.bind('<<ComboboxSelected>>', lambda e: self.on_global_param_change())
        
        # Container principal
        content_frame = ttk.Frame(main_frame)
        content_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # GAUCHE: Liste + Infos
        left_panel = ttk.Frame(content_frame)
        left_panel.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        # Liste images
        list_frame = ttk.LabelFrame(left_panel, text="Images", padding="5")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.image_listbox = tk.Listbox(list_frame, height=20, width=35, selectmode=tk.EXTENDED)
        self.image_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.image_listbox.bind('<<ListboxSelect>>', self.on_image_select)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.image_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.image_listbox.config(yscrollcommand=scrollbar.set)
        

        
        # Boutons sélection rapide
        select_frame = ttk.Frame(list_frame)
        select_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(select_frame, text="✓ Tout", command=self.select_all_images, width=10).pack(side=tk.LEFT, padx=2)
        ttk.Button(select_frame, text="✗ Rien", command=self.deselect_all_images, width=10).pack(side=tk.LEFT, padx=2)
        ttk.Button(select_frame, text="⇄ Inverser", command=self.invert_selection, width=10).pack(side=tk.LEFT, padx=2)
        
        # Bouton réautoriser
        ttk.Button(list_frame, text="🔓 Réautoriser sélection", 
                  command=self.reauthorize_image).pack(pady=5)
        
        # Infos image
        info_frame = ttk.LabelFrame(left_panel, text="Informations Image", padding="5")
        info_frame.pack(fill=tk.X)
        
        self.info_text = tk.Text(info_frame, height=10, width=35, wrap=tk.WORD, state='disabled')
        self.info_text.pack(fill=tk.BOTH, expand=True)
        
        # CENTRE: Previews
        center_panel = ttk.Frame(content_frame)
        center_panel.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        
        # Original
        original_frame = ttk.LabelFrame(center_panel, text="Image Originale", padding="5")
        original_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.canvas_original = Canvas(original_frame, width=640, height=200, bg='black')
        self.canvas_original.pack()
        
        # Status
        status_frame = ttk.Frame(center_panel)
        status_frame.pack(pady=5, fill=tk.X)
        
        self.ia_status_var = tk.StringVar(value="En attente...")
        ttk.Label(status_frame, textvariable=self.ia_status_var,
                 font=('Arial', 10, 'italic')).pack()
        
        # DMD Principal
        dmd_main_frame = ttk.LabelFrame(center_panel, text="Aperçu DMD Principal (128x32)", padding="5")
        dmd_main_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.canvas_dmd_main = Canvas(dmd_main_frame, width=640, height=160, bg='black')
        self.canvas_dmd_main.pack()
        
        # Propositions IA
        proposals_frame = ttk.LabelFrame(center_panel, text="Propositions IA", padding="5")
        proposals_frame.pack(fill=tk.BOTH, expand=True)
        
        self.proposal_canvases = []
        self.proposal_labels = []
        self.proposal_locks = []
        self.proposal_info_labels = []
        
        proposals_grid = ttk.Frame(proposals_frame)
        proposals_grid.pack()
        
        for i in range(5):
            frame = ttk.Frame(proposals_grid, relief=tk.RAISED, borderwidth=2)
            frame.grid(row=0, column=i, padx=5, pady=5)
            
            label = ttk.Label(frame, text=f"Proposition {i+1}", font=('Arial', 8))
            label.pack()
            
            canvas = Canvas(frame, width=256, height=64, cursor='hand2', bg='black')
            canvas.pack()
            canvas.bind('<Button-1>', lambda e, idx=i: self.select_proposal(idx))
            
            # Infos paramètres
            info_label = ttk.Label(frame, text="", font=('Arial', 7), wraplength=250)
            info_label.pack(pady=2)
            
            lock_var = tk.BooleanVar()
            lock_check = ttk.Checkbutton(frame, text="🔒 Verrouiller",
                                        variable=lock_var,
                                        command=lambda idx=i, var=lock_var: self.toggle_lock(idx, var))
            lock_check.pack()
            
            self.proposal_canvases.append(canvas)
            self.proposal_labels.append(label)
            self.proposal_info_labels.append(info_label)
            self.proposal_locks.append(lock_var)
        
        # Boutons action
        action_frame = ttk.Frame(main_frame)
        action_frame.grid(row=3, column=0, columnspan=3, pady=10)
        
        ttk.Button(action_frame, text="🚀 Traiter tout", command=self.process_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="✅ Traiter sélection", command=self.process_selected).pack(side=tk.LEFT, padx=5)
        
        # Configuration grille
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        content_frame.columnconfigure(1, weight=1)
        content_frame.rowconfigure(0, weight=1)
    
    def setup_manual_tab(self):
        """Configuration onglet MANUEL avec effets avancés"""
        main_frame = ttk.Frame(self.manual_frame, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Split horizontal
        left_panel = ttk.Frame(main_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH)
        
        # LEFT: Edition
        toolbar = ttk.Frame(left_panel)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(toolbar, text="📂 Charger", command=self.load_manual_image).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="✂️ Crop 128×32", command=self.start_crop_mode).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="↶ Annuler", command=self.manual_undo).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="💾 Exporter GIF", command=self.manual_export).pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5, fill=tk.Y)
        ttk.Button(toolbar, text="📚 Multi-images", command=self.load_multiple_manual_images).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="🎬 Morphing", command=self.generate_morphing_animation).pack(side=tk.LEFT, padx=2)
        
        # Liste images multiples (sous toolbar)
        self.multi_images_frame = ttk.LabelFrame(left_panel, text="Images chargées (morphing)", padding="5")
        self.multi_images_frame.pack(fill=tk.X, pady=(0, 10))
        self.multi_images_frame.pack_forget()  # Caché par défaut
        
        multi_list_container = ttk.Frame(self.multi_images_frame)
        multi_list_container.pack(fill=tk.BOTH, expand=True)
        
        self.multi_images_listbox = tk.Listbox(multi_list_container, height=4, selectmode=tk.SINGLE)
        self.multi_images_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.multi_images_listbox.bind('<<ListboxSelect>>', self.on_multi_image_select)
        
        multi_scroll = ttk.Scrollbar(multi_list_container, orient=tk.VERTICAL, command=self.multi_images_listbox.yview)
        multi_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.multi_images_listbox.config(yscrollcommand=multi_scroll.set)
        
        multi_btn_frame = ttk.Frame(self.multi_images_frame)
        multi_btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(multi_btn_frame, text="🎬 Morphing", command=self.generate_morphing_animation, width=15).pack(side=tk.LEFT, padx=2)
        ttk.Button(multi_btn_frame, text="🗑️ Effacer", command=self.clear_multi_images, width=15).pack(side=tk.LEFT, padx=2)
        
        self.multi_images = []

        
        # Effets temps réel
        effects_frame = ttk.LabelFrame(left_panel, text="Effets Temps Réel", padding="5")
        effects_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.create_slider(effects_frame, "Luminosité:", 0.5, 2.0, 1.0, 'manual_brightness')
        self.create_slider(effects_frame, "Contraste:", 0.5, 3.0, 1.0, 'manual_contrast')
        self.create_slider(effects_frame, "Saturation:", 0.0, 2.0, 1.0, 'manual_saturation')
        self.create_slider(effects_frame, "Netteté:", 0.0, 3.0, 1.0, 'manual_sharpness')
        
        # Filtres
        filters_frame = ttk.LabelFrame(left_panel, text="Filtres", padding="5")
        filters_frame.pack(fill=tk.X, pady=(0, 10))
        
        filters = [
            ["Flou", "Flou Gaussien", "Contours", "Relief", "Détails+"],
            ["Inverser", "Miroir H", "Miroir V", "Rotation 90°", "N&B"],
            ["Posteriser", "Solariser", "Égaliser", "Auto-contraste", "Resize +"],
            ["Resize -", "", "", "", ""]
        ]
        
        for row_filters in filters:
            row = ttk.Frame(filters_frame)
            row.pack(fill=tk.X, pady=2)
            for f in row_filters:
                if f:
                    ttk.Button(row, text=f, width=15,
                              command=lambda x=f.lower().replace(' ', '_').replace('é', 'e').replace('°', ''):
                              self.apply_filter(x)).pack(side=tk.LEFT, padx=2)
        
        # Outils dessin
        draw_frame = ttk.LabelFrame(left_panel, text="Outils Dessin", padding="5")
        draw_frame.pack(fill=tk.X, pady=(0, 10))
        
        draw_row1 = ttk.Frame(draw_frame)
        draw_row1.pack(fill=tk.X, pady=2)
        
        self.fill_btn = ttk.Button(draw_row1, text="🎨 Remplissage", command=self.toggle_fill_mode)
        self.fill_btn.pack(side=tk.LEFT, padx=2)
        
        self.eraser_btn = ttk.Button(draw_row1, text="🧹 Gomme Magique", command=self.toggle_eraser_mode)
        self.eraser_btn.pack(side=tk.LEFT, padx=2)
        
        ttk.Button(draw_row1, text="Couleur", command=self.choose_fill_color).pack(side=tk.LEFT, padx=2)
        
        self.color_preview = Canvas(draw_row1, width=30, height=20, bg='red')
        self.color_preview.pack(side=tk.LEFT, padx=5)
        
        draw_row2 = ttk.Frame(draw_frame)
        draw_row2.pack(fill=tk.X, pady=2)
        
        ttk.Label(draw_row2, text="Tolérance:").pack(side=tk.LEFT)
        self.fill_tolerance = tk.IntVar(value=30)
        ttk.Spinbox(draw_row2, from_=0, to=100, textvariable=self.fill_tolerance, width=10).pack(side=tk.LEFT, padx=5)
        
        ttk.Checkbutton(draw_row2, text="Fond noir", variable=tk.BooleanVar()).pack(side=tk.LEFT, padx=20)
        

        
        # Canvas édition
        canvas_frame = ttk.LabelFrame(left_panel, text="Édition", padding="5")
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.manual_canvas = Canvas(canvas_frame, width=640, height=480, bg='black', cursor='crosshair')
        self.manual_canvas.pack()
        self.manual_canvas.bind('<Button-1>', self.on_manual_click)
        
        self.manual_status = tk.StringVar(value="Chargez une image")
        ttk.Label(canvas_frame, textvariable=self.manual_status, font=('Arial', 9, 'italic')).pack(pady=5)
        
        # RIGHT: Preview animation

        preview_frame = ttk.LabelFrame(right_panel, text="Aperçu Animation DMD", padding="5")
        preview_frame.pack(fill=tk.BOTH, expand=False)
        
        self.manual_preview_canvas = Canvas(preview_frame, width=512, height=80, bg='black')
        self.manual_preview_canvas.pack(pady=5)
        
        ttk.Button(preview_frame, text="🎬 Prévisualiser", command=self.generate_manual_animation).pack(pady=5)
        
        self.manual_preview_status = tk.StringVar(value="Cliquez Prévisualiser")
        ttk.Label(preview_frame, textvariable=self.manual_preview_status,
                 font=('Arial', 9, 'italic')).pack(pady=5)

        # Animations et paramètres regroupés
        anim_frame = ttk.LabelFrame(right_panel, text="Animations & Paramètres", padding="5")
        anim_frame.pack(fill=tk.X, pady=(0, 10), expand=True)
        
        # Type animation
        row1 = ttk.Frame(anim_frame)
        row1.pack(fill=tk.X, pady=2)
        
        ttk.Label(row1, text="Animation:").pack(side=tk.LEFT)
        self.manual_anim_type = tk.StringVar(value="scroll")
        anim_types = [
            "scroll", "fade_in", "fade_out", "zoom_in", "zoom_out",
            "rotate", "wave", "bounce", "flash", "slide_left",
            "slide_right", "spiral", "shake", "pulse", "glitch",
            "pixelate", "blur_transition", "color_shift"
        ]
        ttk.Combobox(row1, textvariable=self.manual_anim_type, values=anim_types,
                    state="readonly", width=15).pack(side=tk.LEFT, padx=5)
        
        # Direction (pour scroll)
        ttk.Label(row1, text="Direction:").pack(side=tk.LEFT, padx=(20, 5))
        self.manual_direction = tk.StringVar(value="horizontal")
        ttk.Combobox(row1, textvariable=self.manual_direction,
                    values=["horizontal", "vertical"], state="readonly", width=12).pack(side=tk.LEFT)
        
        # Paramètres
        row2 = ttk.Frame(anim_frame)
        row2.pack(fill=tk.X, pady=2)
        
        ttk.Label(row2, text="FPS:").pack(side=tk.LEFT)
        self.manual_fps = tk.IntVar(value=10)
        ttk.Spinbox(row2, from_=1, to=60, textvariable=self.manual_fps, width=10).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(row2, text="Vitesse:").pack(side=tk.LEFT, padx=(20, 5))
        self.manual_scroll_speed = tk.IntVar(value=2)
        ttk.Spinbox(row2, from_=1, to=10, textvariable=self.manual_scroll_speed, width=10).pack(side=tk.LEFT)
        
        ttk.Label(row2, text="Durée (s):").pack(side=tk.LEFT, padx=(20, 5))
        self.manual_duration = tk.DoubleVar(value=2.0)
        ttk.Spinbox(row2, from_=0.1, to=30, increment=0.1, textvariable=self.manual_duration, width=10).pack(side=tk.LEFT)
        # Options boucle
        row3 = ttk.Frame(anim_frame)
        row3.pack(fill=tk.X, pady=2)
        
        ttk.Label(row3, text="Boucle:").pack(side=tk.LEFT)
        self.manual_loop_mode = tk.StringVar(value="normal")
        ttk.Combobox(row3, textvariable=self.manual_loop_mode,
                    values=["normal", "ping-pong", "infini"], state="readonly", width=12).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(row3, text="Répétitions:").pack(side=tk.LEFT, padx=(20, 5))
        self.manual_loop_count = tk.IntVar(value=1)
        ttk.Spinbox(row3, from_=1, to=10, textvariable=self.manual_loop_count, width=10).pack(side=tk.LEFT)
        
        # Contrôles avancés
        advanced_frame = ttk.LabelFrame(anim_frame, text="⚙️ Contrôles Avancés", padding="5")
        advanced_frame.pack(fill=tk.X, pady=(5, 0))
        
        adv_row1 = ttk.Frame(advanced_frame)
        adv_row1.pack(fill=tk.X, pady=2)
        
        ttk.Label(adv_row1, text="Easing:").pack(side=tk.LEFT)
        self.manual_easing = tk.StringVar(value="linear")
        ttk.Combobox(adv_row1, textvariable=self.manual_easing,
                    values=["linear", "ease-in", "ease-out", "ease-in-out", "bounce"], 
                    state="readonly", width=12).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(adv_row1, text="Délai début (s):").pack(side=tk.LEFT, padx=(20, 5))
        self.manual_delay_start = tk.DoubleVar(value=0.0)
        ttk.Spinbox(adv_row1, from_=0.0, to=5.0, increment=0.1, textvariable=self.manual_delay_start, width=8).pack(side=tk.LEFT)
        
        adv_row2 = ttk.Frame(advanced_frame)
        adv_row2.pack(fill=tk.X, pady=2)
        
        self.manual_reverse = tk.BooleanVar(value=False)
        ttk.Checkbutton(adv_row2, text="Inverser direction", variable=self.manual_reverse).pack(side=tk.LEFT, padx=5)
        
        self.manual_bounce_edges = tk.BooleanVar(value=False)
        ttk.Checkbutton(adv_row2, text="Rebond aux bords", variable=self.manual_bounce_edges).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(adv_row2, text="Opacité:").pack(side=tk.LEFT, padx=(20, 5))
        self.manual_opacity = tk.DoubleVar(value=1.0)
        ttk.Scale(adv_row2, from_=0.1, to=1.0, variable=self.manual_opacity, orient=tk.HORIZONTAL, length=100).pack(side=tk.LEFT)
        
        opacity_label = ttk.Label(adv_row2, text="100%", width=5)
        opacity_label.pack(side=tk.LEFT, padx=5)
        self.manual_opacity.trace_add('write', lambda *args: opacity_label.config(text=f"{int(self.manual_opacity.get()*100)}%"))


    
            # INFO PANEL

        
        # Panneau informations image (bas droite, à côté de l'image DMD)
        info_image_frame = ttk.LabelFrame(right_panel, text="ℹ️ Informations Image", padding="5")
        info_image_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self.manual_info_text = tk.Text(info_image_frame, height=8, width=45, wrap=tk.WORD, 
                                        state='disabled', font=('Courier', 9))
        self.manual_info_text.pack(fill=tk.BOTH, expand=True)

    
    def setup_textscroll_tab(self):
        """Configuration onglet TEXTSCROLL avec effets avancés"""
        main_frame = ttk.Frame(self.textscroll_frame, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left: Params
        left_panel = ttk.Frame(main_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Text input
        text_frame = ttk.LabelFrame(left_panel, text="Texte", padding="5")
        text_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.text_input = tk.Text(text_frame, height=4, width=50, wrap=tk.WORD)
        self.text_input.pack(fill=tk.X)
        self.text_input.insert(1.0, "Votre texte ici...")
        self.text_input.bind('<FocusIn>', self.clear_text_placeholder)
        self.text_input.bind('<FocusOut>', self.restore_text_placeholder)
        
        # Font
        font_frame = ttk.LabelFrame(left_panel, text="Police", padding="5")
        font_frame.pack(fill=tk.X, pady=(0, 10))
        
        row1 = ttk.Frame(font_frame)
        row1.pack(fill=tk.X, pady=2)
        
        ttk.Label(row1, text="Famille:").pack(side=tk.LEFT)
        self.text_font_family = tk.StringVar(value="Arial")
        
        # Récupérer vraies polices système
        # TOUTES les polices système (sans filtrage)
        available_fonts = self._get_usable_fonts()
        ttk.Combobox(row1, textvariable=self.text_font_family, values=available_fonts,
                    state="readonly", width=20).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(row1, text="Taille:").pack(side=tk.LEFT, padx=(20, 5))
        self.text_font_size = tk.IntVar(value=20)
        ttk.Spinbox(row1, from_=8, to=48, textvariable=self.text_font_size, width=10).pack(side=tk.LEFT)
        
        row2 = ttk.Frame(font_frame)
        row2.pack(fill=tk.X, pady=2)
        
        self.text_bold = tk.BooleanVar()
        ttk.Checkbutton(row2, text="Gras", variable=self.text_bold).pack(side=tk.LEFT, padx=5)
        
        self.text_italic = tk.BooleanVar()
        ttk.Checkbutton(row2, text="Italique", variable=self.text_italic).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(row2, text="Couleur texte", command=self.choose_text_color).pack(side=tk.LEFT, padx=20)
        self.text_color = (255, 255, 255)
        self.text_color_preview = Canvas(row2, width=30, height=20, bg='white')
        self.text_color_preview.pack(side=tk.LEFT, padx=5)
        
        # Effets texte
        effects_frame = ttk.LabelFrame(left_panel, text="Effets Texte", padding="5")
        effects_frame.pack(fill=tk.X, pady=(0, 10))
        
        row1 = ttk.Frame(effects_frame)
        row1.pack(fill=tk.X, pady=2)
        
        ttk.Label(row1, text="Effet:").pack(side=tk.LEFT)
        self.text_effect = tk.StringVar(value="normal")
        text_effects = [
            "normal", "3d", "fire", "snow", "ice", "metal",
            "neon", "graffiti", "pixel_art", "outline", "shadow"
        ]
        ttk.Combobox(row1, textvariable=self.text_effect, values=text_effects,
                    state="readonly", width=15).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(row1, text="Couleur fond", command=self.choose_text_bg).pack(side=tk.LEFT, padx=20)
        self.text_bg_color = (0, 0, 0)
        self.text_bg_preview = Canvas(row1, width=30, height=20, bg='black')
        self.text_bg_preview.pack(side=tk.LEFT, padx=5)
        
        # Effets couleur
        row2 = ttk.Frame(effects_frame)
        row2.pack(fill=tk.X, pady=2)
        
        ttk.Label(row2, text="Effet couleur:").pack(side=tk.LEFT)
        self.text_color_effect = tk.StringVar(value="none")
        color_effects = ["none", "rainbow", "matrix", "fire", "gradient"]
        ttk.Combobox(row2, textvariable=self.text_color_effect, values=color_effects,
                    state="readonly", width=15).pack(side=tk.LEFT, padx=5)
        
        # Animation
        anim_frame = ttk.LabelFrame(left_panel, text="Animation", padding="5")
        anim_frame.pack(fill=tk.X, pady=(0, 10))
        
        row1 = ttk.Frame(anim_frame)
        row1.pack(fill=tk.X, pady=2)
        
        ttk.Label(row1, text="Type:").pack(side=tk.LEFT)
        self.text_anim_type = tk.StringVar(value="scroll_horizontal")
        text_anims = [
            "scroll_horizontal", "scroll_vertical", "scroll_wave",
            "starwars", "bounce_scroll", "typewriter", "explode",
            "matrix_rain", "spiral", "shake", "glitch", "fade_in", "static"
        ]
        ttk.Combobox(row1, textvariable=self.text_anim_type, values=text_anims,
                    state="readonly", width=20).pack(side=tk.LEFT, padx=5)
        
        row2 = ttk.Frame(anim_frame)
        row2.pack(fill=tk.X, pady=2)
        
        ttk.Label(row2, text="FPS:").pack(side=tk.LEFT)
        self.text_fps = tk.IntVar(value=10)
        ttk.Spinbox(row2, from_=1, to=60, textvariable=self.text_fps, width=10).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(row2, text="Vitesse:").pack(side=tk.LEFT, padx=(20, 5))
        self.text_speed = tk.IntVar(value=2)
        ttk.Spinbox(row2, from_=1, to=10, textvariable=self.text_speed, width=10).pack(side=tk.LEFT)
        
        ttk.Label(row2, text="Durée (s):").pack(side=tk.LEFT, padx=(20, 5))
        self.text_duration = tk.DoubleVar(value=3.0)
        ttk.Spinbox(row2, from_=1.0, to=30, increment=0.5, textvariable=self.text_duration, width=10).pack(side=tk.LEFT)
        
        ttk.Checkbutton(row2, text="Auto-ajuster", variable=tk.BooleanVar(value=True)).pack(side=tk.LEFT, padx=20)
        
        # Buttons
        btn_frame = ttk.Frame(left_panel)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="🎬 Générer Preview", command=self.generate_text_preview).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="💾 Exporter GIF", command=self.export_text_gif).pack(side=tk.LEFT, padx=5)
        
        # Right: Preview
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH)
        
        preview_frame = ttk.LabelFrame(right_panel, text="Aperçu Animation", padding="5")
        preview_frame.pack(fill=tk.BOTH, expand=False)
        
        self.text_preview_canvas = Canvas(preview_frame, width=512, height=128, bg='black')
        self.text_preview_canvas.pack(pady=10)
        
        self.text_preview_status = tk.StringVar(value="Entrez du texte et générez")
        ttk.Label(preview_frame, textvariable=self.text_preview_status,
                 font=('Arial', 9, 'italic')).pack(pady=5)
        
        # Infos GIF
        self.text_gif_info = tk.StringVar(value="")
        ttk.Label(preview_frame, textvariable=self.text_gif_info,
                 font=('Arial', 8)).pack(pady=5)
        
        # Appliquer police à la zone texte en temps réel
        self.text_font_family.trace_add('write', lambda *args: self.apply_font_to_textbox())
        self.text_font_size.trace_add('write', lambda *args: self.apply_font_to_textbox())
        self.text_bold.trace_add('write', lambda *args: self.apply_font_to_textbox())
        self.text_italic.trace_add('write', lambda *args: self.apply_font_to_textbox())
        
        # Appliquer police initiale
        self.apply_font_to_textbox()

    
    def setup_params_tab(self):
        """Configuration onglet PARAMETRES"""
        main_frame = ttk.Frame(self.params_frame, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Thème
        theme_frame = ttk.LabelFrame(main_frame, text="Apparence", padding="10")
        theme_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(theme_frame, text="Thème:").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(theme_frame, text="🌙 Sombre", variable=self.theme, value="dark",
                       command=self.apply_theme).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(theme_frame, text="☀️ Clair", variable=self.theme, value="light",
                       command=self.apply_theme).pack(side=tk.LEFT, padx=10)
        
        # Comportement
        behavior_frame = ttk.LabelFrame(main_frame, text="Comportement", padding="10")
        behavior_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Checkbutton(behavior_frame, text="Ajouter type d'animation au nom de fichier",
                       variable=self.add_anim_to_name).pack(anchor=tk.W, pady=5)
        
        # Export
        export_frame = ttk.LabelFrame(main_frame, text="Export", padding="10")
        export_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(export_frame, text="Qualité par défaut:").pack(anchor=tk.W, pady=5)
        
        quality_frame = ttk.Frame(export_frame)
        quality_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(quality_frame, text="Couleurs GIF:").pack(side=tk.LEFT)
        self.default_colors = tk.IntVar(value=256)
        ttk.Combobox(quality_frame, textvariable=self.default_colors,
                    values=[8, 16, 32, 64, 128, 256], state="readonly", width=10).pack(side=tk.LEFT, padx=5)
        
        # Cache
        cache_frame = ttk.LabelFrame(main_frame, text="Performance", padding="10")
        cache_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Checkbutton(cache_frame, text="Activer cache IA",
                       variable=tk.BooleanVar(value=True)).pack(anchor=tk.W, pady=5)
        
        ttk.Button(cache_frame, text="🗑️ Vider cache", command=self.clear_cache).pack(anchor=tk.W, pady=5)
        
        # Logs
        logs_frame = ttk.LabelFrame(main_frame, text="Logs", padding="10")
        logs_frame.pack(fill=tk.X)
        
        ttk.Checkbutton(logs_frame, text="Sauvegarder logs automatiquement",
                       variable=tk.BooleanVar(value=False)).pack(anchor=tk.W, pady=5)
        
        ttk.Button(logs_frame, text="📄 Exporter logs", command=self.export_logs).pack(anchor=tk.W, pady=5)
    
    def setup_debug_tab(self):
        """Configuration onglet DEBUG"""
        main_frame = ttk.Frame(self.debug_frame, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        toolbar = ttk.Frame(main_frame)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(toolbar, text="🗑️ Effacer logs", command=self.clear_logs).pack(side=tk.LEFT, padx=5)
        
        self.autoscroll_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(toolbar, text="Auto-scroll", variable=self.autoscroll_var).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(toolbar, text="Filtrer:").pack(side=tk.LEFT, padx=(20, 5))
        self.log_filter = tk.StringVar(value="ALL")
        ttk.Combobox(toolbar, textvariable=self.log_filter,
                    values=["ALL", "INFO", "WARNING", "ERROR", "DEBUG"],
                    state="readonly", width=10).pack(side=tk.LEFT)
        
        log_frame = ttk.Frame(main_frame)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = tk.Text(log_frame, wrap=tk.WORD, height=30, bg='#1a1a1a', fg='#00ff00',
                               font=('Courier', 9))
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        log_scroll = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        log_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=log_scroll.set)
        
        self.log_text.tag_config('INFO', foreground='#00ff00')
        self.log_text.tag_config('WARNING', foreground='#ffaa00')
        self.log_text.tag_config('ERROR', foreground='#ff0000')
        self.log_text.tag_config('DEBUG', foreground='#00aaff')
        
        logger.callbacks.append(self.add_log_entry)
    
    # ========================================================================
    # HELPERS UI
    # ========================================================================
    
    def create_slider(self, parent, label, from_, to, default, var_name):
        """Crée un slider avec label et valeur"""
        row = ttk.Frame(parent)
        row.pack(fill=tk.X, pady=2)
        ttk.Label(row, text=label, width=12).pack(side=tk.LEFT)
        var = tk.DoubleVar(value=default)
        setattr(self, var_name, var)
        ttk.Scale(row, from_=from_, to=to, variable=var,
                 command=lambda v: self.apply_manual_effect()).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        value_label = ttk.Label(row, text=f"{default:.2f}", width=5)
        value_label.pack(side=tk.LEFT)
        var.trace_add('write', lambda *args: value_label.config(text=f"{var.get():.2f}"))
    
    def add_log_entry(self, entry):
        """Ajoute une entrée de log dans l'interface"""
        filter_level = self.log_filter.get()
        if filter_level != "ALL" and entry['level'] != filter_level:
            return
        
        self.log_text.insert(tk.END, f"[{entry['time']}] ", 'INFO')
        self.log_text.insert(tk.END, f"{entry['level']}: ", entry['level'])
        self.log_text.insert(tk.END, f"{entry['message']}\n")
        
        if self.autoscroll_var.get():
            self.log_text.see(tk.END)
    
    def clear_logs(self):
        """Efface tous les logs"""
        self.log_text.delete(1.0, tk.END)
        logger.logs.clear()
        logger.info("Logs effacés")
    
    def apply_theme(self):
        """Applique le thème sélectionné avec plus de variété"""
        style = ttk.Style()
        
        if self.theme.get() == "dark":
            # Palette sombre variée
            bg_main = '#1e1e1e'
            bg_secondary = '#2d2d2d'
            bg_input = '#3c3c3c'
            fg_main = '#e0e0e0'
            fg_accent = '#4a9eff'
            border = '#555555'
            select_bg = '#0d47a1'
            
            self.root.configure(bg=bg_main)
            style.theme_use('clam')
            
            style.configure('.', background=bg_main, foreground=fg_main,
                          fieldbackground=bg_input, bordercolor=border)
            style.configure('TFrame', background=bg_main)
            style.configure('TLabel', background=bg_main, foreground=fg_main)
            style.configure('TLabelframe', background=bg_secondary, foreground=fg_accent, borderwidth=2)
            style.configure('TLabelframe.Label', background=bg_secondary, foreground=fg_accent, font=('Arial', 9, 'bold'))
            style.configure('TButton', background=bg_input, foreground=fg_main, borderwidth=1, relief=tk.RAISED)
            style.map('TButton', background=[('active', '#4a4a4a'), ('pressed', '#5a5a5a')])
            style.configure('TCheckbutton', background=bg_main, foreground=fg_main)
            style.configure('TRadiobutton', background=bg_main, foreground=fg_main)
            style.configure('TNotebook', background=bg_main, borderwidth=0)
            style.configure('TNotebook.Tab', background=bg_secondary, foreground=fg_main, padding=[10, 5])
            style.map('TNotebook.Tab', background=[('selected', bg_input)], foreground=[('selected', fg_accent)])
            
            if hasattr(self, 'canvas_original'):
                self.canvas_original.configure(bg='#0a0a0a')
                self.canvas_dmd_main.configure(bg='black')
                self.image_listbox.configure(bg=bg_input, fg=fg_main, selectbackground=select_bg, selectforeground='white')
                
                for canvas in self.proposal_canvases:
                    canvas.configure(bg='black')
        else:
            # Palette claire variée
            bg_main = '#f5f5f5'
            bg_secondary = '#ffffff'
            bg_input = '#ffffff'
            fg_main = '#212121'
            fg_accent = '#1976d2'
            border = '#bdbdbd'
            select_bg = '#bbdefb'
            
            self.root.configure(bg=bg_main)
            style.theme_use('clam')
            
            style.configure('.', background=bg_main, foreground=fg_main,
                          fieldbackground=bg_input, bordercolor=border)
            style.configure('TFrame', background=bg_main)
            style.configure('TLabel', background=bg_main, foreground=fg_main)
            style.configure('TLabelframe', background=bg_secondary, foreground=fg_accent, borderwidth=2)
            style.configure('TLabelframe.Label', background=bg_secondary, foreground=fg_accent, font=('Arial', 9, 'bold'))
            style.configure('TButton', background='#e0e0e0', foreground=fg_main, borderwidth=1, relief=tk.RAISED)
            style.map('TButton', background=[('active', '#d0d0d0'), ('pressed', '#c0c0c0')])
            style.configure('TCheckbutton', background=bg_main, foreground=fg_main)
            style.configure('TRadiobutton', background=bg_main, foreground=fg_main)
            style.configure('TNotebook', background=bg_main, borderwidth=0)
            style.configure('TNotebook.Tab', background='#e0e0e0', foreground=fg_main, padding=[10, 5])
            style.map('TNotebook.Tab', background=[('selected', bg_secondary)], foreground=[('selected', fg_accent)])
            
            if hasattr(self, 'canvas_original'):
                self.canvas_original.configure(bg='#fafafa')
                self.canvas_dmd_main.configure(bg='black')
                self.image_listbox.configure(bg=bg_input, fg=fg_main, selectbackground=select_bg, selectforeground=fg_main)
                
                for canvas in self.proposal_canvases:
                    canvas.configure(bg='black')
        
        logger.debug(f"Thème appliqué: {self.theme.get()}")
    
    # ========================================================================
    # ONGLET AUTO - Gestion
    # ========================================================================
    
    def on_tab_changed(self, event):
        """Callback changement d'onglet"""
        current_tab = self.notebook.index(self.notebook.select())
        
        # Si passage à MANUEL, charger image AUTO si sélectionnée
        if current_tab == 1 and self.current_image_idx is not None:
            self.load_from_auto()
    
    def select_folder(self):
        """Sélectionne un dossier source"""
        folder = filedialog.askdirectory()
        if folder:
            self.load_images_from_folder(folder)
            logger.info(f"Dossier: {folder}")
    
    def select_images(self):
        """Sélectionne des images individuelles"""
        files = filedialog.askopenfilenames(
            filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        if files:
            self.images = list(files)
            self.update_listbox()
            logger.info(f"{len(files)} images chargées")
    
    def load_images_from_folder(self, folder):
        """Charge images depuis un dossier"""
        self.images = []
        pattern = "**/*" if self.recursive_var.get() else "*"
        for ext in ['png', 'jpg', 'jpeg', 'bmp', 'gif']:
            self.images.extend(Path(folder).glob(f"{pattern}.{ext}"))
        self.images = [str(p) for p in self.images]
        self.update_listbox()
        logger.info(f"{len(self.images)} images trouvées")
    
    def update_listbox(self):
        """Met à jour la liste d'images"""
        self.image_listbox.delete(0, tk.END)
        for i, img in enumerate(self.images):
            name = Path(img).name
            prefix = ""
            color = None
            
            if img in self.manual_exports:
                prefix = "✓ "
                color = 'green'
            elif img in self.image_settings:
                prefix = "⚙ "
                color = 'orange'
            
            self.image_listbox.insert(tk.END, prefix + name)
            if color:
                self.image_listbox.itemconfig(i, fg=color)
        
        self.progress_var.set(f"{len(self.images)} images | {len(self.manual_exports)} manuelles")
    
    def reauthorize_image(self):
        """Réautorise une image exclue (retirée des exports manuels)"""
        selection = self.image_listbox.curselection()
        if not selection:
            messagebox.showwarning("Attention", "Sélectionnez une image")
            return
        
        img_path = self.images[selection[0]]
        if img_path in self.manual_exports:
            self.manual_exports.remove(img_path)
            self.update_listbox()
            messagebox.showinfo("Succès", f"{Path(img_path).name} réautorisée pour traitement AUTO")
            logger.info(f"Réautorisée: {Path(img_path).name}")
        else:
            messagebox.showinfo("Info", "Cette image n'est pas exclue")
    
    def on_image_select(self, event):
        """Callback sélection d'image dans la liste"""
        selection = self.image_listbox.curselection()
        if selection:
            idx = selection[0]
            self.current_image_idx = idx
            img_path = self.images[idx]
            
            self.animating = False
            threading.Thread(target=lambda: self.auto_analyze_and_preview(img_path), daemon=True).start()
    
    def on_global_param_change(self):
        """Callback changement paramètres globaux - relance IA"""
        if self.current_image_idx is not None:
            img_path = self.images[self.current_image_idx]
            threading.Thread(target=lambda: self.auto_analyze_and_preview(img_path), daemon=True).start()
    
    def show_original(self, image_path):
        """Affiche l'image originale"""
        img_orig = Image.open(image_path).convert('RGB')
        w, h = img_orig.size
        scale = min(640/w, 200/h)
        display_w, display_h = int(w*scale), int(h*scale)
        img_display = img_orig.resize((display_w, display_h), Image.Resampling.LANCZOS)
        
        self.preview_original = ImageTk.PhotoImage(img_display)
        self.canvas_original.delete("all")
        self.canvas_original.create_image(320, 100, image=self.preview_original)
    
    def update_image_info(self, image_path):
        """Met à jour les informations de l'image"""
        img = Image.open(image_path)
        file_size = Path(image_path).stat().st_size / 1024  # KB
        
        # Détecter palette
        palette = DMDEngine.detect_palette(img, max_colors=8)
        palette_str = ", ".join([f"RGB{c}" for c in palette[:3]]) + "..."
        
        info = f"""Fichier: {Path(image_path).name}
Format: {img.format}
Dimensions: {img.size[0]} x {img.size[1]} px
Mode: {img.mode}
Taille: {file_size:.1f} KB

Palette dominante:
{palette_str}

Ratio: {img.size[0]/img.size[1]:.2f}
Cible DMD: 4.0 (128/32)
"""
        
        self.info_text.config(state='normal')
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, info)
        self.info_text.config(state='disabled')
    
    def auto_analyze_and_preview(self, image_path):
        """Analyse IA et génération des propositions"""
        try:
            self.ia_status_var.set("🔍 Analyse en cours...")
            self.root.update()
            
            # Afficher original et infos
            self.show_original(image_path)
            self.update_image_info(image_path)
            
            img = Image.open(image_path)
            analysis = {'size': img.size}
            
            self.ia_status_var.set("🤖 Génération propositions IA...")
            self.root.update()
            
            # Générer variantes
            variants = self.generate_settings_variants(analysis)
            
            self.ia_status_var.set("📊 Évaluation qualité...")
            self.root.update()
            
            # Évaluer chaque variante
            scored_variants = []
            for v in variants:
                canvas, _ = self.render_dmd_frame(image_path, v, return_frames=False)
                score = self.evaluate_quality(img, canvas)
                scored_variants.append((score, v, canvas))
            
            # Trier par score (meilleur = score le plus bas)
            scored_variants.sort(key=lambda x: x[0])
            self.proposals = [(v, c) for _, v, c in scored_variants]
            
            # Afficher propositions
            for i, (variant, canvas) in enumerate(self.proposals):
                display = canvas.resize((256, 64), Image.Resampling.NEAREST)
                photo = ImageTk.PhotoImage(display)
                self.proposal_canvases[i].delete("all")
                self.proposal_canvases[i].create_image(128, 32, image=photo)
                self.proposal_canvases[i].image = photo
                self.proposal_labels[i].config(text=f"{i+1}. {variant['name']}")
                
                # Afficher infos paramètres
                info_text = f"Contraste: {variant['contrast']:.1f}\n"
                info_text += f"Saturation: {variant['saturation']:.1f}\n"
                info_text += f"FPS: {variant['fps']} | Vitesse: {variant['scroll_speed']}\n"
                info_text += f"Direction: {variant['direction']}"
                self.proposal_info_labels[i].config(text=info_text)
            
            # Sélectionner meilleure
            self.selected_proposal = 0
            self.highlight_proposal(0)
            
            # Sauvegarder settings
            self.image_settings[image_path] = self.proposals[0][0].copy()
            
            best_settings = self.image_settings[image_path]
            
            self.ia_status_var.set(f"✓ Meilleure: '{self.proposals[0][0]['name']}' (score: {scored_variants[0][0]:.1f})")
            
            # Lancer preview animé
            self.start_continuous_preview(image_path, best_settings)
            logger.info(f"Analyse terminée: {Path(image_path).name}")
            
        except Exception as e:
            self.ia_status_var.set(f"❌ Erreur: {str(e)}")
            logger.error(f"Erreur analyse: {e}")
    
    def generate_settings_variants(self, analysis):
        """Génère 5 variantes de paramètres basées sur l'analyse"""
        w, h = analysis['size']
        ratio = w / h
        target_ratio = 128 / 32
        
        # Paramètres globaux
        base_fps = self.fps_var.get()
        base_duration = self.duration_var.get()
        base_scroll = self.scroll_speed_var.get()
        base_contrast = self.contrast_var.get()
        base_saturation = self.saturation_var.get()
        
        variants = []
        
        # 1. Conservateur (préserve proportions)
        variants.append({
            'name': 'Conservateur',
            'resize_mode': 'fit',
            'contrast': base_contrast * 0.9,
            'saturation': base_saturation * 0.9,
            'brightness': 1.0,
            'black_threshold': 35,
            'fps': base_fps,
            'scroll_speed': base_scroll,
            'duration': base_duration,
            'direction': 'auto'
        })
        
        # 2. Remplissage (remplit écran)
        variants.append({
            'name': 'Remplissage',
            'resize_mode': 'fill',
            'contrast': base_contrast,
            'saturation': base_saturation,
            'brightness': 1.0,
            'black_threshold': 30,
            'fps': base_fps,
            'scroll_speed': base_scroll,
            'duration': base_duration,
            'direction': 'auto'
        })
        
        # 3. Contraste+ (pour images fades)
        variants.append({
            'name': 'Contraste+',
            'resize_mode': 'auto',
            'contrast': base_contrast * 1.3,
            'saturation': base_saturation * 1.2,
            'brightness': 1.0,
            'black_threshold': 40,
            'fps': base_fps,
            'scroll_speed': base_scroll,
            'duration': base_duration,
            'direction': 'auto'
        })
        
        # 4. Fluide (animation douce)
        variants.append({
            'name': 'Fluide',
            'resize_mode': 'fill',
            'contrast': base_contrast * 0.95,
            'saturation': base_saturation,
            'brightness': 1.0,
            'black_threshold': 30,
            'fps': int(base_fps * 1.5),
            'scroll_speed': max(1, base_scroll - 1),
            'duration': base_duration * 1.2,
            'direction': 'horizontal' if ratio > target_ratio else 'vertical'
        })
        
        # 5. Équilibré (compromis)
        variants.append({
            'name': 'Équilibré',
            'resize_mode': 'auto',
            'contrast': base_contrast,
            'saturation': base_saturation,
            'brightness': 1.0,
            'black_threshold': 30,
            'fps': base_fps,
            'scroll_speed': base_scroll,
            'duration': base_duration,
            'direction': 'auto'
        })
        
        return variants
    
    def evaluate_quality(self, original_img, dmd_canvas):
        """Évalue la qualité d'une conversion (score bas = meilleur)"""
        # Redimensionner original à 128x32 pour comparaison
        orig_resized = original_img.convert('RGB').resize((128, 32), Image.Resampling.LANCZOS)
        
        arr_orig = np.array(orig_resized).astype(float)
        arr_dmd = np.array(dmd_canvas.convert('RGB')).astype(float)
        
        # Différence moyenne
        diff = np.mean(np.abs(arr_orig - arr_dmd))
        
        # Pénalité pour trop de blanc (artefacts)
        white_orig = np.sum(np.all(arr_orig > 240, axis=2))
        white_dmd = np.sum(np.all(arr_dmd > 240, axis=2))
        white_penalty = max(0, white_dmd - white_orig) * 5
        
        return diff + white_penalty
    
    def render_dmd_frame(self, image_path, settings, return_frames=False):
        """Rend une image en DMD avec les paramètres donnés"""
        img_orig = Image.open(image_path)
        
        # Détecter fond
        bg_color, is_dark = DMDEngine.detect_background_color(img_orig)
        
        # Optimiser pour DMD
        img = DMDEngine.optimize_for_dmd(img_orig, settings)
        
        # Redimensionner adaptatif
        img, new_w, new_h = DMDEngine.adaptive_resize(img, 128, 32, settings['resize_mode'])
        
        if not return_frames:
            # Retourner frame unique
            canvas = Image.new('RGB', (128, 32), bg_color)
            x = (128 - new_w) // 2
            y = (32 - new_h) // 2
            canvas.paste(img, (x, y))
            return canvas, settings['fps']
        
        # Générer animation
        frames, direction = DMDEngine.create_animation_frames(img, settings, bg_color)
        
        return frames, settings['fps']
    
    def start_continuous_preview(self, image_path, settings):
        """Lance la preview animée continue"""
        self.animating = False
        time.sleep(0.1)
        
        try:
            frames, fps = self.render_dmd_frame(image_path, settings, return_frames=True)
            self.preview_frames = frames
            self.preview_index = 0
            self.animating = True
            self.current_fps = fps
            self.root.after(0, self.animate_preview)
        except Exception as e:
            self.ia_status_var.set(f"❌ Erreur preview: {str(e)}")
            logger.error(f"Erreur preview: {e}")
    
    def animate_preview(self):
        """Animation de la preview principale"""
        if not self.animating or not self.preview_frames:
            return
        
        try:
            frame = self.preview_frames[self.preview_index]
            display = frame.resize((640, 160), Image.Resampling.NEAREST)
            self.preview_dmd = ImageTk.PhotoImage(display)
            self.canvas_dmd_main.delete("all")
            self.canvas_dmd_main.create_image(320, 80, image=self.preview_dmd)
            
            self.preview_index = (self.preview_index + 1) % len(self.preview_frames)
            delay = int(1000 / self.current_fps) if self.current_fps > 0 else 100
            self.root.after(delay, self.animate_preview)
        except:
            self.animating = False
    
    def highlight_proposal(self, idx):
        """Met en surbrillance la proposition sélectionnée"""
        for i, canvas in enumerate(self.proposal_canvases):
            parent = canvas.master
            if i == idx:
                parent.config(relief=tk.SOLID, borderwidth=3)
                if self.theme.get() == "dark":
                    self.proposal_labels[i].config(foreground='#00ff00', font=('Arial', 8, 'bold'))
                else:
                    self.proposal_labels[i].config(foreground='green', font=('Arial', 8, 'bold'))
            else:
                parent.config(relief=tk.RAISED, borderwidth=2)
                if self.theme.get() == "dark":
                    self.proposal_labels[i].config(foreground='#ffffff', font=('Arial', 8))
                else:
                    self.proposal_labels[i].config(foreground='black', font=('Arial', 8))
    
    def select_proposal(self, idx):
        """Sélectionne une proposition IA"""
        if idx >= len(self.proposals):
            return
        
        self.selected_proposal = idx
        self.highlight_proposal(idx)
        
        if self.current_image_idx is not None:
            img_path = self.images[self.current_image_idx]
            settings = self.proposals[idx][0].copy()
            self.image_settings[img_path] = settings
            
            self.ia_status_var.set(f"👤 Sélection manuelle: '{settings['name']}'")
            self.start_continuous_preview(img_path, settings)
            logger.info(f"Proposition {idx+1} sélectionnée")
    
    def toggle_lock(self, idx, var):
        """Verrouille/déverrouille une proposition pour batch"""
        if var.get():
            # Déverrouiller les autres
            for i, lock in enumerate(self.proposal_locks):
                if i != idx:
                    lock.set(False)
            self.locked_proposal = idx
            self.ia_status_var.set(f"🔒 Proposition {idx+1} verrouillée pour batch")
            logger.info(f"Proposition {idx+1} verrouillée")
        else:
            self.locked_proposal = None
            self.ia_status_var.set("🔓 Déverrouillé")
            logger.info("Déverrouillé")
    
    def get_settings_for_image(self, image_path):
        """Récupère les settings optimaux pour une image"""
        # Si proposition verrouillée, utiliser celle-ci
        if self.locked_proposal is not None and self.proposals:
            return self.proposals[self.locked_proposal][0].copy()
        
        # Si settings déjà calculés, les utiliser
        if image_path in self.image_settings:
            return self.image_settings[image_path]
        
        # Sinon, calculer à la volée
        img = Image.open(image_path)
        analysis = {'size': img.size}
        variants = self.generate_settings_variants(analysis)
        
        # Évaluer et prendre le meilleur
        scored = []
        for v in variants:
            canvas, _ = self.render_dmd_frame(image_path, v, return_frames=False)
            score = self.evaluate_quality(img, canvas)
            scored.append((score, v))
        
        scored.sort(key=lambda x: x[0])
        return scored[0][1].copy()
    
    def process_images(self, image_list):
        """Traite un lot d'images"""
        output_dir = filedialog.askdirectory(title="Dossier de sortie")
        if not output_dir:
            return
        
        # Vérifier dossiers différents
        if self.images:
            input_dir = str(Path(self.images[0]).parent)
            if Path(input_dir).resolve() == Path(output_dir).resolve():
                messagebox.showerror("Erreur", "Les dossiers d'entrée et sortie doivent être différents")
                logger.error("Dossiers identiques")
                return
        
        # Vérifier dossier non vide
        if list(Path(output_dir).glob('*')):
            if not messagebox.askyesno("Confirmation",
                                      "Le dossier de sortie n'est pas vide. Continuer ?"):
                logger.warning("Batch annulé: dossier non vide")
                return
        
        # Filtrer exports manuels
        to_process = [img for img in image_list if img not in self.manual_exports]
        
        if len(to_process) < len(image_list):
            skipped = len(image_list) - len(to_process)
            logger.warning(f"{skipped} images ignorées (exports manuels)")
        
        total = len(to_process)
        for i, img_path in enumerate(to_process):
            self.progress_var.set(f"Traitement {i+1}/{total}: {Path(img_path).name}")
            self.root.update()
            
            try:
                settings = self.get_settings_for_image(img_path)
                frames, fps = self.render_dmd_frame(img_path, settings, return_frames=True)
                
                # Détecter vraie direction utilisée
                _, actual_direction = DMDEngine.create_animation_frames(
                    Image.open(img_path), settings, (0, 0, 0)
                )
                
                # Nom fichier
                stem = Path(img_path).stem
                if self.add_anim_to_name.get():
                    output_name = f"{stem}_{actual_direction}_dmd.gif"
                else:
                    output_name = f"{stem}_dmd.gif"
                
                output_path = Path(output_dir) / output_name
                
                # Adapter palette selon source
                img_source = Image.open(img_path)
                source_palette = DMDEngine.detect_palette(img_source, max_colors=16)
                
                # Choisir nombre de couleurs adapté
                if len(source_palette) <= 8:
                    color_count = 8
                elif len(source_palette) <= 16:
                    color_count = 16
                else:
                    color_count = self.color_count_var.get()
                
                # Conversion palette
                p_frames = []
                for frame in frames:
                    p_frame = frame.convert('P', palette=Image.ADAPTIVE, colors=color_count,
                                           dither=Image.Dither.FLOYDSTEINBERG)
                    p_frames.append(p_frame)
                
                # Export
                p_frames[0].save(
                    output_path,
                    save_all=True,
                    append_images=p_frames[1:],
                    duration=int(1000/fps),
                    loop=0 if self.manual_loop_mode.get() == "infini" else self.manual_loop_count.get(),
                    optimize=True
                )
                logger.info(f"GIF créé: {output_name} ({len(frames)} frames, {color_count} couleurs)")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur sur {Path(img_path).name}: {e}")
                logger.error(f"Erreur {Path(img_path).name}: {e}")
        
        self.progress_var.set(f"Terminé: {total} GIF créés")
        messagebox.showinfo("Succès", f"{total} GIF créés dans {output_dir}")
        logger.info(f"Batch terminé: {total} GIF")
    
    def process_all(self):
        """Traite toutes les images"""
        if not self.images:
            messagebox.showwarning("Attention", "Aucune image chargée")
            return
        threading.Thread(target=lambda: self.process_images(self.images), daemon=True).start()
    
    def process_selected(self):
        """Traite les images sélectionnées"""
        selection = self.image_listbox.curselection()
        if not selection:
            messagebox.showwarning("Attention", "Sélectionnez des images")
            return
        selected = [self.images[i] for i in selection]
        threading.Thread(target=lambda: self.process_images(selected), daemon=True).start()
    
    # ========================================================================
    # ONGLET MANUEL
    # ========================================================================
    
    def load_from_auto(self):
        """Charge l'image sélectionnée dans AUTO vers MANUEL"""
        if self.current_image_idx is None:
            return
        
        img_path = self.images[self.current_image_idx]
        self.manual_image = Image.open(img_path).convert('RGB')
        self.manual_original = self.manual_image.copy()
        self.manual_history = [self.manual_image.copy()]
        
        # Reset sliders
        self.manual_brightness.set(1.0)
        self.manual_contrast.set(1.0)
        self.manual_saturation.set(1.0)
        self.manual_sharpness.set(1.0)
        
        self.display_manual_image()
        self.manual_status.set(f"Image: {Path(img_path).name}")
        logger.info(f"Image chargée en manuel: {Path(img_path).name}")
    
    def load_manual_image(self):
        """Charge une image manuellement"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        if file_path:
            self.manual_image = Image.open(file_path).convert('RGB')
            self.manual_original = self.manual_image.copy()
            self.manual_history = [self.manual_image.copy()]
            
            self.manual_brightness.set(1.0)
            self.manual_contrast.set(1.0)
            self.manual_saturation.set(1.0)
            self.manual_sharpness.set(1.0)
            
            self.display_manual_image()
            self.manual_status.set(f"Image: {Path(file_path).name}")
            logger.info(f"Image chargée: {Path(file_path).name}")
    
    def display_manual_image(self):
        """Affiche l'image dans le canvas manuel"""
        if self.manual_image is None:
            return
        
        w, h = self.manual_image.size
        scale = min(640/w, 320/h)
        display_w, display_h = int(w*scale), int(h*scale)
        img_display = self.manual_image.resize((display_w, display_h), Image.Resampling.LANCZOS)
        
        self.manual_preview = ImageTk.PhotoImage(img_display)
        self.manual_canvas.delete("all")
        self.manual_canvas.create_image(320, 160, image=self.manual_preview)
        self.update_manual_info()
    
    def apply_manual_effect(self):
        """Applique les effets temps réel (sliders)"""
        if self.manual_image is None or not self.manual_history:
            return
        
        base_img = self.manual_history[0].copy()
        
        if self.manual_brightness.get() != 1.0:
            enhancer = ImageEnhance.Brightness(base_img)
            base_img = enhancer.enhance(self.manual_brightness.get())
        
        if self.manual_contrast.get() != 1.0:
            enhancer = ImageEnhance.Contrast(base_img)
            base_img = enhancer.enhance(self.manual_contrast.get())
        
        if self.manual_saturation.get() != 1.0:
            enhancer = ImageEnhance.Color(base_img)
            base_img = enhancer.enhance(self.manual_saturation.get())
        
        if self.manual_sharpness.get() != 1.0:
            enhancer = ImageEnhance.Sharpness(base_img)
            base_img = enhancer.enhance(self.manual_sharpness.get())
        
        self.manual_image = base_img
        self.display_manual_image()
    
    def apply_filter(self, filter_name):
        """Applique un filtre"""
        if self.manual_image is None:
            return
        
        self.manual_history.append(self.manual_image.copy())
        
        filters_map = {
            'flou': ImageFilter.BLUR,
            'flou_gaussien': lambda: ImageFilter.GaussianBlur(radius=2),
            'contours': ImageFilter.FIND_EDGES,
            'relief': ImageFilter.EMBOSS,
            'details+': ImageFilter.DETAIL,
        }
        
        if filter_name in filters_map:
            f = filters_map[filter_name]
            self.manual_image = self.manual_image.filter(f() if callable(f) else f)
        elif filter_name == 'inverser':
            self.manual_image = ImageOps.invert(self.manual_image)
        elif filter_name == 'miroir_h':
            self.manual_image = ImageOps.mirror(self.manual_image)
        elif filter_name == 'miroir_v':
            self.manual_image = ImageOps.flip(self.manual_image)
        elif filter_name == 'rotation_90':
            self.manual_image = self.manual_image.rotate(90, expand=True)
        elif filter_name == 'n&b':
            self.manual_image = ImageOps.grayscale(self.manual_image).convert('RGB')
        elif filter_name == 'posteriser':
            self.manual_image = ImageOps.posterize(self.manual_image, 4)
        elif filter_name == 'solariser':
            self.manual_image = ImageOps.solarize(self.manual_image, threshold=128)
        elif filter_name == 'egaliser':
            self.manual_image = ImageOps.equalize(self.manual_image)
        elif filter_name == 'auto-contraste':
            self.manual_image = ImageOps.autocontrast(self.manual_image)
        
        elif filter_name == 'resize_+':
            w, h = self.manual_image.size
            self.manual_image = self.manual_image.resize((int(w*1.2), int(h*1.2)), Image.Resampling.LANCZOS)
        elif filter_name == 'resize_-':
            w, h = self.manual_image.size
            self.manual_image = self.manual_image.resize((int(w*0.8), int(h*0.8)), Image.Resampling.LANCZOS)
        
        self.display_manual_image()
        logger.info(f"Filtre appliqué: {filter_name}")
    
    def manual_undo(self):
        """Annule la dernière action"""
        if len(self.manual_history) > 1:
            self.manual_history.pop()
            self.manual_image = self.manual_history[-1].copy()
            self.display_manual_image()
            self.manual_status.set("Annulation effectuée")
            logger.info("Annulation")
        else:
            messagebox.showinfo("Info", "Rien à annuler")
    
    def toggle_fill_mode(self):
        """Active/désactive le mode remplissage"""
        self.fill_mode = not self.fill_mode
        self.eraser_mode = False
        
        if self.fill_mode:
            self.fill_btn.config(text="🎨 Remplissage (ACTIF)")
            self.eraser_btn.config(text="🧹 Gomme Magique")
            self.manual_canvas.config(cursor='crosshair')
            self.manual_status.set("Mode remplissage actif - Cliquez sur une zone")
            logger.info("Remplissage ON")
        else:
            self.fill_btn.config(text="🎨 Remplissage")
            self.manual_canvas.config(cursor='arrow')
            self.manual_status.set("Mode remplissage OFF")
            logger.info("Remplissage OFF")
    
    def toggle_eraser_mode(self):
        """Active/désactive la gomme magique"""
        self.eraser_mode = not self.eraser_mode
        self.fill_mode = False
        
        if self.eraser_mode:
            self.eraser_btn.config(text="🧹 Gomme Magique (ACTIF)")
            self.fill_btn.config(text="🎨 Remplissage")
            self.manual_canvas.config(cursor='crosshair')
            self.manual_status.set("Gomme magique active - Cliquez pour effacer")
            logger.info("Gomme magique ON")
        else:
            self.eraser_btn.config(text="🧹 Gomme Magique")
            self.manual_canvas.config(cursor='arrow')
            self.manual_status.set("Gomme magique OFF")
            logger.info("Gomme magique OFF")
    
    def choose_fill_color(self):
        """Choisit la couleur de remplissage"""
        color = colorchooser.askcolor(title="Couleur remplissage", initialcolor=self.fill_color)
        if color[0]:
            self.fill_color = tuple(int(c) for c in color[0])
            hex_color = '#%02x%02x%02x' % self.fill_color
            self.color_preview.config(bg=hex_color)
            logger.info(f"Couleur remplissage: {self.fill_color}")
    
    def on_manual_click(self, event):
        """Gère les clics sur le canvas manuel"""
        if self.manual_image is None:
            return
        
        # Convertir coordonnées canvas vers image
        w, h = self.manual_image.size
        scale = min(640/w, 320/h)
        display_w, display_h = int(w*scale), int(h*scale)
        
        offset_x = (640 - display_w) // 2
        offset_y = (320 - display_h) // 2
        
        click_x = event.x - offset_x
        click_y = event.y - offset_y
        
        if click_x < 0 or click_x >= display_w or click_y < 0 or click_y >= display_h:
            return
        
        # Coordonnées dans l'image originale
        img_x = int(click_x / scale)
        img_y = int(click_y / scale)
        
        if self.fill_mode:
            self.flood_fill(img_x, img_y)
        elif self.eraser_mode:
            self.magic_eraser(img_x, img_y)
    
    def flood_fill(self, x, y):
        """Remplissage par diffusion"""
        self.manual_history.append(self.manual_image.copy())
        
        arr = np.array(self.manual_image)
        h, w = arr.shape[:2]
        
        if x < 0 or x >= w or y < 0 or y >= h:
            return
        
        target_color = tuple(arr[y, x])
        tolerance = self.fill_tolerance.get()
        
        # BFS flood fill
        visited = set()
        queue = [(x, y)]
        
        while queue:
            cx, cy = queue.pop(0)
            
            if (cx, cy) in visited:
                continue
            if cx < 0 or cx >= w or cy < 0 or cy >= h:
                continue
            
            current_color = tuple(arr[cy, cx])
            
            # Vérifier similarité
            diff = sum(abs(a - b) for a, b in zip(current_color, target_color))
            if diff > tolerance:
                continue
            
            visited.add((cx, cy))
            arr[cy, cx] = self.fill_color
            
            # Ajouter voisins
            queue.extend([(cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)])
        
        self.manual_image = Image.fromarray(arr)
        self.display_manual_image()
        self.manual_status.set(f"Remplissage: {len(visited)} pixels")
        logger.info(f"Remplissage: {len(visited)} pixels")
    
    def magic_eraser(self, x, y):
        """Gomme magique - efface couleur similaire"""
        self.manual_history.append(self.manual_image.copy())
        
        arr = np.array(self.manual_image)
        h, w = arr.shape[:2]
        
        if x < 0 or x >= w or y < 0 or y >= h:
            return
        
        target_color = tuple(arr[y, x])
        tolerance = self.fill_tolerance.get()
        
        # Trouver tous les pixels similaires
        erased = 0
        for py in range(h):
            for px in range(w):
                current_color = tuple(arr[py, px])
                diff = sum(abs(a - b) for a, b in zip(current_color, target_color))
                if diff <= tolerance:
                    arr[py, px] = [0, 0, 0]  # Noir
                    erased += 1
        
        self.manual_image = Image.fromarray(arr)
        self.display_manual_image()
        self.manual_status.set(f"Gomme: {erased} pixels effacés")
        logger.info(f"Gomme magique: {erased} pixels")
    
    def generate_manual_animation(self):
        """Génère l'animation avec les paramètres manuels"""
        if self.manual_image is None:
            messagebox.showwarning("Attention", "Chargez une image d'abord")
            return
        
        self.manual_animating = False
        time.sleep(0.1)
        
        try:
            anim_type = self.manual_anim_type.get()
            fps = self.manual_fps.get()
            duration = self.manual_duration.get()
            speed = self.manual_scroll_speed.get()
            direction = self.manual_direction.get()
            
            # Redimensionner pour DMD
            img_resized, new_w, new_h = DMDEngine.adaptive_resize(self.manual_image, 128, 32, 'auto')
            
            # Générer frames selon type
            if anim_type == 'scroll':
                self.manual_frames = ManualEffects.scroll_effect(img_resized, direction, speed, duration, fps)
            elif anim_type == 'fade_in':
                self.manual_frames = ManualEffects.fade_effect(img_resized, duration, fps, fade_in=True)
            elif anim_type == 'fade_out':
                self.manual_frames = ManualEffects.fade_effect(img_resized, duration, fps, fade_in=False)
            elif anim_type == 'zoom_in':
                self.manual_frames = ManualEffects.zoom_effect(img_resized, duration, fps, zoom_in=True)
            elif anim_type == 'zoom_out':
                self.manual_frames = ManualEffects.zoom_effect(img_resized, duration, fps, zoom_in=False)
            elif anim_type == 'rotate':
                self.manual_frames = ManualEffects.rotate_effect(img_resized, duration, fps)
            elif anim_type == 'wave':
                self.manual_frames = ManualEffects.wave_effect(img_resized, duration, fps)
            elif anim_type == 'bounce':
                self.manual_frames = ManualEffects.bounce_effect(img_resized, duration, fps)
            elif anim_type == 'flash':
                self.manual_frames = ManualEffects.flash_effect(img_resized, duration, fps)
            elif anim_type == 'slide_left':
                self.manual_frames = ManualEffects.slide_effect(img_resized, 'left', duration, fps)
            elif anim_type == 'slide_right':
                self.manual_frames = ManualEffects.slide_effect(img_resized, 'right', duration, fps)
            elif anim_type == 'spiral':
                self.manual_frames = ManualEffects.spiral_effect(img_resized, duration, fps)
            elif anim_type == 'shake':
                self.manual_frames = ManualEffects.shake_effect(img_resized, duration, fps)
            elif anim_type == 'pulse':
                self.manual_frames = ManualEffects.pulse_effect(img_resized, duration, fps)
            elif anim_type == 'glitch':
                self.manual_frames = ManualEffects.glitch_effect(img_resized, duration, fps)
            elif anim_type == 'pixelate':
                self.manual_frames = ManualEffects.pixelate_effect(img_resized, duration, fps)
            elif anim_type == 'blur_transition':
                self.manual_frames = ManualEffects.blur_transition_effect(img_resized, duration, fps)
            elif anim_type == 'color_shift':
                self.manual_frames = ManualEffects.color_shift_effect(img_resized, duration, fps)
            else:
                self.manual_frames = [img_resized]
            

            
            # Appliquer mode boucle
            loop_mode = self.manual_loop_mode.get()
            loop_count = self.manual_loop_count.get()
            
            if loop_mode == "ping-pong":
                # Ajouter frames inversées (sans dupliquer première/dernière)
                reversed_frames = self.manual_frames[-2:0:-1]
                self.manual_frames = self.manual_frames + reversed_frames
            
            if loop_mode == "infini" or loop_count > 1:
                # Répéter frames
                original_frames = self.manual_frames.copy()
                for _ in range(loop_count - 1):
                    self.manual_frames.extend(original_frames)

            self.manual_frame_idx = 0
            self.manual_animating = True
            self.manual_preview_status.set(f"Animation: {len(self.manual_frames)} frames @ {fps} FPS")
            self.root.after(0, self.animate_manual_preview)
            
            logger.info(f"Animation générée: {anim_type}, {len(self.manual_frames)} frames")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur génération: {e}")
            logger.error(f"Erreur animation manuelle: {e}")
    
    def animate_manual_preview(self):
        """Animation de la preview manuelle"""
        if not self.manual_animating or not self.manual_frames:
            return
        
        try:
            frame = self.manual_frames[self.manual_frame_idx]
            display = frame.resize((512, 128), Image.Resampling.NEAREST)
            self.manual_preview_photo = ImageTk.PhotoImage(display)
            self.manual_preview_canvas.delete("all")
            self.manual_preview_canvas.create_image(256, 64, image=self.manual_preview_photo)
            
            self.manual_frame_idx = (self.manual_frame_idx + 1) % len(self.manual_frames)
            delay = int(1000 / self.manual_fps.get())
            self.root.after(delay, self.animate_manual_preview)
        except:
            self.manual_animating = False
    
    def manual_export(self):
        """Exporte le GIF manuel"""
        if not self.manual_frames:
            messagebox.showwarning("Attention", "Générez d'abord une animation")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".gif",
            filetypes=[("GIF", "*.gif")]
        )
        
        if not file_path:
            return
        
        try:
            fps = self.manual_fps.get()
            color_count = self.color_count_var.get()
            
            # Conversion palette
            p_frames = []
            for frame in self.manual_frames:
                p_frame = frame.convert('P', palette=Image.ADAPTIVE, colors=color_count,
                                       dither=Image.Dither.FLOYDSTEINBERG)
                p_frames.append(p_frame)
            
            # Export
            p_frames[0].save(
                file_path,
                save_all=True,
                append_images=p_frames[1:],
                duration=int(1000/fps),
                loop=0 if self.manual_loop_mode.get() == "infini" else self.manual_loop_count.get(),
                optimize=True
            )
            
            # Marquer comme export manuel
            if self.current_image_idx is not None:
                img_path = self.images[self.current_image_idx]
                self.manual_exports.add(img_path)
                self.update_listbox()
            
            file_size = Path(file_path).stat().st_size / 1024
            messagebox.showinfo("Succès", f"GIF exporté: {Path(file_path).name}\n{file_size:.1f} KB")
            logger.info(f"Export manuel: {Path(file_path).name}, {file_size:.1f} KB")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur export: {e}")
            logger.error(f"Erreur export manuel: {e}")
    
    # ========================================================================
    # ONGLET TEXTSCROLL
    # ========================================================================
    
    
    def apply_font_to_textbox(self):
        """Applique la police à la zone de texte"""
        try:
            family = self.text_font_family.get()
            size = self.text_font_size.get()
            weight = 'bold' if self.text_bold.get() else 'normal'
            slant = 'italic' if self.text_italic.get() else 'roman'
            self.text_input.config(font=(family, size, weight, slant))
        except:
            pass
    
    def clear_text_placeholder(self, event):
        """Efface le placeholder au focus"""
        if self.text_input.get(1.0, tk.END).strip() == "Votre texte ici...":
            self.text_input.delete(1.0, tk.END)
    
    def restore_text_placeholder(self, event):
        """Restaure le placeholder si vide"""
        if not self.text_input.get(1.0, tk.END).strip():
            self.text_input.insert(1.0, "Votre texte ici...")
    
    def choose_text_color(self):
        """Choisit la couleur du texte"""
        color = colorchooser.askcolor(title="Couleur texte", initialcolor=self.text_color)
        if color[0]:
            self.text_color = tuple(int(c) for c in color[0])
            hex_color = '#%02x%02x%02x' % self.text_color
            self.text_color_preview.config(bg=hex_color)
            logger.info(f"Couleur texte: {self.text_color}")
    
    def choose_text_bg(self):
        """Choisit la couleur de fond"""
        color = colorchooser.askcolor(title="Couleur fond", initialcolor=self.text_bg_color)
        if color[0]:
            self.text_bg_color = tuple(int(c) for c in color[0])
            hex_color = '#%02x%02x%02x' % self.text_bg_color
            self.text_bg_preview.config(bg=hex_color)
            logger.info(f"Couleur fond: {self.text_bg_color}")
    

    def render_text_image(self):
        """Rend le texte en image avec effets"""
        text = self.text_input.get(1.0, tk.END).strip()
        if not text or text == "Votre texte ici...":
            return None
        
        font = self.get_text_font()
        effect = self.text_effect.get()
        color_effect = self.text_color_effect.get()
        
        # Créer image large pour le texte
        img = Image.new('RGB', (2000, 32), self.text_bg_color)
        draw = ImageDraw.Draw(img)
        
        # Appliquer effet texte
        if effect == '3d':
            TextEffects.effect_3d(draw, text, (10, 8), font, self.text_color, self.text_bg_color)
        elif effect == 'fire':
            TextEffects.effect_fire(draw, text, (10, 8), font)
        elif effect == 'ice':
            TextEffects.effect_ice(draw, text, (10, 8), font)
        elif effect == 'metal':
            TextEffects.effect_metal(draw, text, (10, 8), font)
        elif effect == 'neon':
            TextEffects.effect_neon(draw, text, (10, 8), font, self.text_color)
        elif effect == 'graffiti':
            TextEffects.effect_graffiti(draw, text, (10, 8), font)
        elif effect == 'outline':
            # Contour
            for dx in [-2, -1, 0, 1, 2]:
                for dy in [-2, -1, 0, 1, 2]:
                    if dx != 0 or dy != 0:
                        draw.text((10 + dx, 8 + dy), text, fill=(0, 0, 0), font=font)
            draw.text((10, 8), text, fill=self.text_color, font=font)
        elif effect == 'shadow':
            # Ombre
            draw.text((12, 10), text, fill=(0, 0, 0), font=font)
            draw.text((10, 8), text, fill=self.text_color, font=font)
        else:
            # Normal
            if color_effect == 'rainbow':
                TextEffects.effect_rainbow(draw, text, (10, 8), font)
            elif color_effect == 'matrix':
                TextEffects.effect_matrix(draw, text, (10, 8), font)
            elif color_effect == 'fire':
                TextEffects.effect_fire(draw, text, (10, 8), font)
            elif color_effect == 'gradient':
                TextEffects.effect_gradient(draw, text, (10, 8), font, self.text_color, (255, 255, 0))
            else:
                draw.text((10, 8), text, fill=self.text_color, font=font)
        
        # Appliquer effets post-traitement
        if effect == 'snow':
            img = TextEffects.effect_snow(img, img)
        elif effect == 'pixel_art':
            img = TextEffects.effect_pixel_art(img)
        
        # Recadrer au contenu
        bbox = img.getbbox()
        if bbox:
            img = img.crop((bbox[0] - 10, 0, bbox[2] + 10, 32))
        
        return img
    
    def generate_text_preview(self):
        """Génère la preview du texte animé"""
        self.text_animating = False
        time.sleep(0.1)
        
        try:
            text_img = self.render_text_image()
            if text_img is None:
                messagebox.showwarning("Attention", "Entrez du texte")
                return
            
            anim_type = self.text_anim_type.get()
            fps = self.text_fps.get()
            speed = self.text_speed.get()
            duration = self.text_duration.get()
            
            # Auto-ajuster durée selon longueur texte
            text_length = len(self.text_input.get(1.0, tk.END).strip())
            if text_length > 50:
                duration = max(duration, text_length / 10)
            
            font = self.get_text_font()
            
            # Générer animation
            if anim_type == 'scroll_horizontal':
                self.text_frames = ManualEffects.scroll_effect(text_img, 'horizontal', speed, duration, fps)
            elif anim_type == 'scroll_vertical':
                self.text_frames = ManualEffects.scroll_effect(text_img, 'vertical', speed, duration, fps)
            elif anim_type == 'scroll_wave':
                self.text_frames = TextAnimations.scroll_wave(text_img, duration, fps)
            elif anim_type == 'starwars':
                self.text_frames = TextAnimations.starwars_scroll(text_img, duration, fps)
            elif anim_type == 'bounce_scroll':
                self.text_frames = TextAnimations.bounce_scroll(text_img, duration, fps)
            elif anim_type == 'typewriter':
                text = self.text_input.get(1.0, tk.END).strip()
                self.text_frames = TextAnimations.typewriter(text, font, self.text_color, self.text_bg_color, duration, fps)
            elif anim_type == 'explode':
                self.text_frames = TextAnimations.explode(text_img, duration, fps)
            elif anim_type == 'matrix_rain':
                text = self.text_input.get(1.0, tk.END).strip()
                self.text_frames = TextAnimations.matrix_rain(text, font, duration, fps)
            elif anim_type == 'spiral':
                self.text_frames = TextAnimations.spiral_text(text_img, duration, fps)
            elif anim_type == 'shake':
                self.text_frames = TextAnimations.shake_text(text_img, duration, fps)
            elif anim_type == 'glitch':
                self.text_frames = TextAnimations.glitch_text(text_img, duration, fps)
            elif anim_type == 'fade_in':
                self.text_frames = ManualEffects.fade_effect(text_img, duration, fps, fade_in=True)
            elif anim_type == 'static':
                canvas = Image.new('RGB', (128, 32), self.text_bg_color)
                w, h = text_img.size
                canvas.paste(text_img, ((128 - w) // 2, 0))
                self.text_frames = [canvas] * int(fps * duration)
            else:
                self.text_frames = [text_img]
            
            self.text_frame_idx = 0
            self.text_animating = True
            
            # Calculer infos GIF
            total_frames = len(self.text_frames)
            estimated_size = total_frames * 128 * 32 * 3 / 1024  # Estimation grossière
            
            self.text_preview_status.set(f"Animation: {total_frames} frames @ {fps} FPS")
            self.text_gif_info.set(f"Durée: {duration:.1f}s | Taille estimée: {estimated_size:.1f} KB")
            
            self.root.after(0, self.animate_text_preview)
            logger.info(f"Texte animé: {anim_type}, {total_frames} frames")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur génération texte: {e}")
            logger.error(f"Erreur texte: {e}")
    
    def animate_text_preview(self):
        """Animation de la preview texte"""
        if not self.text_animating or not self.text_frames:
            return
        
        try:
            frame = self.text_frames[self.text_frame_idx]
            display = frame.resize((512, 128), Image.Resampling.NEAREST)
            self.text_preview_photo = ImageTk.PhotoImage(display)
            self.text_preview_canvas.delete("all")
            self.text_preview_canvas.create_image(256, 64, image=self.text_preview_photo)
            
            self.text_frame_idx = (self.text_frame_idx + 1) % len(self.text_frames)
            delay = int(1000 / self.text_fps.get())
            self.root.after(delay, self.animate_text_preview)
        except:
            self.text_animating = False
    
    def export_text_gif(self):
        """Exporte le GIF texte"""
        if not self.text_frames:
            messagebox.showwarning("Attention", "Générez d'abord une preview")
            return
        
        # Nom par défaut: 40 premiers caractères du texte
        text = self.text_input.get(1.0, tk.END).strip()
        default_name = text[:40].replace(' ', '_').replace('\n', '_') + "_dmd.gif"
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".gif",
            initialfile=default_name,
            filetypes=[("GIF", "*.gif")]
        )
        
        if not file_path:
            return
        
        try:
            fps = self.text_fps.get()
            color_count = self.color_count_var.get()
            
            # Conversion palette
            p_frames = []
            for frame in self.text_frames:
                p_frame = frame.convert('P', palette=Image.ADAPTIVE, colors=color_count,
                                       dither=Image.Dither.FLOYDSTEINBERG)
                p_frames.append(p_frame)
            
            # Export
            p_frames[0].save(
                file_path,
                save_all=True,
                append_images=p_frames[1:],
                duration=int(1000/fps),
                loop=0 if self.manual_loop_mode.get() == "infini" else self.manual_loop_count.get(),
                optimize=True
            )
            
            file_size = Path(file_path).stat().st_size / 1024
            messagebox.showinfo("Succès", f"GIF texte exporté: {Path(file_path).name}\n{file_size:.1f} KB")
            logger.info(f"Export texte: {Path(file_path).name}, {file_size:.1f} KB")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur export: {e}")
            logger.error(f"Erreur export texte: {e}")
    
    # ========================================================================
    # PARAMETRES
    # ========================================================================
    
    def clear_cache(self):
        """Vide le cache"""
        self.image_settings.clear()
        self.proposals.clear()
        messagebox.showinfo("Succès", "Cache vidé")
        logger.info("Cache vidé")
    
    def export_logs(self):
        """Exporte les logs"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile=f"dmd_logs_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            filetypes=[("Text", "*.txt")]
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                for entry in logger.logs:
                    f.write(f"[{entry['time']}] {entry['level']}: {entry['message']}\n")
            
            messagebox.showinfo("Succès", f"Logs exportés: {Path(file_path).name}")
            logger.info(f"Logs exportés: {file_path}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur export logs: {e}")
    
    # ========================================================================
    # MAIN
    # ========================================================================
    
    def run(self):
        """Lance l'application"""
        self.root.mainloop()


# ============================================================================
# POINT D'ENTRÉE
# ============================================================================


    def update_manual_info(self):
        """Met à jour les informations de l'image manuelle"""
        if not self.manual_image:
            self.manual_info_text.config(state='normal')
            self.manual_info_text.delete(1.0, tk.END)
            self.manual_info_text.insert(1.0, "Aucune image chargée")
            self.manual_info_text.config(state='disabled')
            return
        
        w, h = self.manual_image.size
        mode = self.manual_image.mode
        
        # Calculer taille mémoire approximative
        pixel_count = w * h
        if mode == 'RGB':
            mem_size = pixel_count * 3
        elif mode == 'RGBA':
            mem_size = pixel_count * 4
        else:
            mem_size = pixel_count
        
        mem_kb = mem_size / 1024
        
        # Palette dominante
        try:
            palette = DMDEngine.detect_palette(self.manual_image, max_colors=8)
            palette_str = "\n".join([f"  RGB{c}" for c in palette[:5]])
        except:
            palette_str = "  N/A"
        
        # Ratio vs DMD
        ratio = w / h if h > 0 else 0
        target_ratio = 128 / 32
        ratio_diff = abs(ratio - target_ratio)
        ratio_status = "✓ Optimal" if ratio_diff < 0.5 else "⚠ Ajuster"
        
        info = f"""Dimensions: {w} × {h} px
Mode couleur: {mode}
Mémoire: {mem_kb:.1f} KB
Ratio: {ratio:.2f} (cible: 4.0)
Status: {ratio_status}

Palette dominante:
{palette_str}

Historique: {len(self.manual_history)} états
"""
        
        self.manual_info_text.config(state='normal')
        self.manual_info_text.delete(1.0, tk.END)
        self.manual_info_text.insert(1.0, info)
        self.manual_info_text.config(state='disabled')



    def apply_font_to_textbox(self, event=None):
        """Applique la police sélectionnée à la zone de texte"""
        family = self.text_font_family.get()
        size = max(8, min(16, self.text_font_size.get() - 4))  # Adapter pour lisibilité
        
        weight = 'bold' if self.text_bold.get() else 'normal'
        slant = 'italic' if self.text_italic.get() else 'roman'
        
        try:
            import tkinter.font as tkfont
            font = tkfont.Font(family=family, size=size, weight=weight, slant=slant)
            self.text_input.config(font=font)
            logger.debug(f"Police appliquée à la zone texte: {family} {size}pt")
        except Exception as e:
            logger.warning(f"Impossible d'appliquer la police: {e}")

    # ========================================================================
    # NOUVELLES MÉTHODES - CROP MODE
    # ========================================================================
    
    def start_crop_mode(self):
        """Active le mode sélection de zone"""
        if self.manual_image is None:
            messagebox.showwarning("Attention", "Chargez une image d'abord")
            return
        
        self.crop_mode = not self.crop_mode
        
        if self.crop_mode:
            self.fill_mode = False
            self.eraser_mode = False
            self.fill_btn.config(text="🎨 Remplissage")
            self.eraser_btn.config(text="🧹 Gomme Magique")
            
            self.manual_canvas.config(cursor='crosshair')
            self.manual_canvas.unbind('<Button-1>')
            self.manual_canvas.bind('<ButtonPress-1>', self.on_crop_start)
            self.manual_canvas.bind('<B1-Motion>', self.on_crop_drag)
            self.manual_canvas.bind('<ButtonRelease-1>', self.on_crop_end)
            self.manual_status.set("Mode crop: tracez un rectangle (ratio 4:1 automatique)")
            logger.info("Crop mode ON")
        else:
            self.manual_canvas.config(cursor='arrow')
            self.manual_canvas.unbind('<ButtonPress-1>')
            self.manual_canvas.unbind('<B1-Motion>')
            self.manual_canvas.unbind('<ButtonRelease-1>')
            self.manual_canvas.bind('<Button-1>', self.on_manual_click)
            if self.crop_preview_rect:
                self.manual_canvas.delete(self.crop_preview_rect)
                self.crop_preview_rect = None
            self.manual_status.set("Crop mode OFF")
            logger.info("Crop mode OFF")
    
    def on_crop_start(self, event):
        """Début sélection crop"""
        self.crop_start = (event.x, event.y)
        if self.crop_preview_rect:
            self.manual_canvas.delete(self.crop_preview_rect)
    
    def on_crop_drag(self, event):
        """Drag sélection crop avec ratio 4:1"""
        if self.crop_start:
            if self.crop_preview_rect:
                self.manual_canvas.delete(self.crop_preview_rect)
            
            x1, y1 = self.crop_start
            width = abs(event.x - x1)
            height = width / 4  # Ratio fixe 128:32
            
            x2 = x1 + width if event.x > x1 else x1 - width
            y2 = y1 + height if event.y > y1 else y1 - height
            
            self.crop_preview_rect = self.manual_canvas.create_rectangle(
                x1, y1, x2, y2, outline='red', width=2, dash=(5, 5)
            )
    
    def on_crop_end(self, event):
        """Fin sélection crop - applique le crop"""
        if not self.crop_start or not self.manual_image:
            return
        
        # Convertir coords canvas → image
        w, h = self.manual_image.size
        scale = min(640/w, 320/h)
        display_w, display_h = int(w*scale), int(h*scale)
        offset_x = (640 - display_w) // 2
        offset_y = (320 - display_h) // 2
        
        x1 = int((self.crop_start[0] - offset_x) / scale)
        y1 = int((self.crop_start[1] - offset_y) / scale)
        x2 = int((event.x - offset_x) / scale)
        y2 = int((event.y - offset_y) / scale)
        
        # Normaliser
        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)
        
        # Forcer ratio 4:1
        crop_w = x2 - x1
        crop_h = int(crop_w / 4)
        
        # Limiter aux bords
        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(w, x1 + crop_w)
        y2 = min(h, y1 + crop_h)
        
        if x2 - x1 < 10 or y2 - y1 < 10:
            messagebox.showwarning("Attention", "Zone trop petite")
            self.manual_canvas.delete(self.crop_preview_rect)
            self.crop_preview_rect = None
            self.crop_start = None
            return
        
        # Appliquer crop
        self.manual_history.append(self.manual_image.copy())
        self.manual_image = self.manual_image.crop((x1, y1, x2, y2))
        
        self.display_manual_image()
        self.manual_canvas.delete(self.crop_preview_rect)
        self.crop_preview_rect = None
        self.crop_start = None
        self.crop_mode = False
        self.manual_canvas.config(cursor='arrow')
        self.manual_canvas.bind('<Button-1>', self.on_manual_click)
        
        self.manual_status.set(f"Crop appliqué: {x2-x1}×{y2-y1}px")
        logger.info(f"Crop: {x2-x1}×{y2-y1}")
    
    # ========================================================================
    # NOUVELLES MÉTHODES - SÉLECTION AUTO
    # ========================================================================
    
    def select_all_images(self):
        """Sélectionne toutes les images"""
        self.image_listbox.selection_set(0, tk.END)
        logger.info("Toutes les images sélectionnées")
    
    def deselect_all_images(self):
        """Désélectionne toutes les images"""
        self.image_listbox.selection_clear(0, tk.END)
        logger.info("Sélection effacée")
    
    def invert_selection(self):
        """Inverse la sélection"""
        current = set(self.image_listbox.curselection())
        all_indices = set(range(len(self.images)))
        new_selection = all_indices - current
        
        self.image_listbox.selection_clear(0, tk.END)
        for idx in new_selection:
            self.image_listbox.selection_set(idx)
        
        logger.info(f"Sélection inversée: {len(new_selection)} images")

    # ========================================================================
    # MÉTHODES - MULTI-IMAGES ET MORPHING
    # ========================================================================
    
    def load_multiple_manual_images(self):
        """Charge plusieurs images pour morphing"""
        files = filedialog.askopenfilenames(
            title="Sélectionner images pour morphing",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        
        if files:
            self.multi_images = []
            self.multi_images_listbox.delete(0, tk.END)
            
            for file in files:
                try:
                    img = Image.open(file).convert('RGB')
                    self.multi_images.append(img)
                    self.multi_images_listbox.insert(tk.END, Path(file).name)
                except Exception as e:
                    logger.error(f"Erreur chargement {file}: {e}")
            
            if self.multi_images:
                self.multi_images_frame.pack(fill=tk.X, pady=(0, 10))
                self.manual_status.set(f"{len(self.multi_images)} images chargées pour morphing")
                logger.info(f"{len(self.multi_images)} images chargées")
                
                # Charger première image
                self.manual_image = self.multi_images[0].copy()
                self.manual_original = self.manual_image.copy()
                self.display_manual_image()
    
    def on_multi_image_select(self, event):
        """Callback sélection image dans liste multi"""
        selection = self.multi_images_listbox.curselection()
        if selection and self.multi_images:
            idx = selection[0]
            self.manual_image = self.multi_images[idx].copy()
            self.manual_original = self.manual_image.copy()
            self.display_manual_image()
            self.manual_status.set(f"Image {idx+1}/{len(self.multi_images)}")
    
    def clear_multi_images(self):
        """Efface la liste multi-images"""
        self.multi_images = []
        self.multi_images_listbox.delete(0, tk.END)
        self.multi_images_frame.pack_forget()
        self.manual_status.set("Liste multi-images effacée")
        logger.info("Multi-images effacées")
    
    def generate_morphing_animation(self):
        """Génère une animation de morphing entre les images"""
        if len(self.multi_images) < 2:
            messagebox.showwarning("Attention", "Chargez au moins 2 images pour le morphing")
            return
        
        self.manual_status.set("Génération morphing...")
        self.root.update()
        
        try:
            fps = self.manual_fps.get()
            transition_frames = int(fps * 1.0)  # 1 seconde par transition
            
            self.manual_frames = []
            
            # Redimensionner toutes les images à la même taille
            target_size = self.multi_images[0].size
            resized_images = [img.resize(target_size, Image.Resampling.LANCZOS) for img in self.multi_images]
            
            # Générer transitions entre chaque paire
            for i in range(len(resized_images) - 1):
                img1 = np.array(resized_images[i])
                img2 = np.array(resized_images[i + 1])
                
                # Interpolation linéaire
                for frame_idx in range(transition_frames):
                    alpha = frame_idx / transition_frames
                    blended = (img1 * (1 - alpha) + img2 * alpha).astype(np.uint8)
                    
                    # Centrer sur canvas DMD
                    canvas = Image.new('RGB', (128, 32), (0, 0, 0))
                    blended_img = Image.fromarray(blended)
                    
                    # Redimensionner pour DMD
                    w, h = blended_img.size
                    scale = min(128/w, 32/h)
                    new_w, new_h = int(w*scale), int(h*scale)
                    blended_img = blended_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                    
                    x = (128 - new_w) // 2
                    y = (32 - new_h) // 2
                    canvas.paste(blended_img, (x, y))
                    
                    self.manual_frames.append(canvas)
                
                # Ajouter image finale (pause)
                for _ in range(int(fps * 0.5)):
                    canvas = Image.new('RGB', (128, 32), (0, 0, 0))
                    img_final = resized_images[i + 1]
                    w, h = img_final.size
                    scale = min(128/w, 32/h)
                    new_w, new_h = int(w*scale), int(h*scale)
                    img_final = img_final.resize((new_w, new_h), Image.Resampling.LANCZOS)
                    x = (128 - new_w) // 2
                    y = (32 - new_h) // 2
                    canvas.paste(img_final, (x, y))
                    self.manual_frames.append(canvas)
            
            # Lancer animation
            self.manual_frame_idx = 0
            self.manual_animating = True
            self.animate_manual_preview()
            
            self.manual_preview_status.set(f"Morphing: {len(self.manual_frames)} frames, {len(self.multi_images)} images")
            self.manual_status.set("Morphing généré !")
            logger.info(f"Morphing: {len(self.manual_frames)} frames")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur génération morphing:\n{e}")
            logger.error(f"Erreur morphing: {e}")
            self.manual_status.set("Erreur morphing")

    def _build_font_registry(self):
        """Cache famille→fichier via registre Windows"""
        if hasattr(self, '_font_registry_cache'):
            return self._font_registry_cache
        
        registry = {}
        fonts_dir = Path("C:/Windows/Fonts")
        
        try:
            import winreg
            key_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts"
            
            for hive in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
                try:
                    key = winreg.OpenKey(hive, key_path)
                except (FileNotFoundError, OSError):
                    continue
                
                i = 0
                while True:
                    try:
                        name, value, _ = winreg.EnumValue(key, i)
                        i += 1
                    except OSError:
                        break
                    
                    if not name or '(TrueType)' not in name and '(OpenType)' not in name:
                        continue
                    
                    # "Arial Bold (TrueType)" → "Arial Bold"
                    full_name = re.sub(r'\s*\((?:TrueType|OpenType)\)\s*$', '', name).strip()
                    
                    # Résoudre chemin
                    if Path(value).is_absolute():
                        filepath = Path(value)
                    else:
                        filepath = fonts_dir / value
                    
                    if not filepath.exists():
                        continue
                    
                    # Détecter style
                    name_lower = full_name.lower()
                    is_bold = 'bold' in name_lower or 'gras' in name_lower
                    is_italic = 'italic' in name_lower or 'oblique' in name_lower or 'italique' in name_lower
                    
                    # Extraire famille (sans Bold/Italic)
                    family = full_name
                    for kw in ['Bold Italic', 'Gras Italique', 'Bold Oblique', 'Bold', 'Gras', 'Italic', 'Italique', 'Oblique', 'Regular']:
                        family = re.sub(r'\s+' + re.escape(kw) + r'$', '', family, flags=re.IGNORECASE)
                    family = family.strip()
                    
                    fl = family.lower()
                    if fl not in registry:
                        registry[fl] = {}
                    registry[fl][(is_bold, is_italic)] = filepath
                
                try:
                    winreg.CloseKey(key)
                except:
                    pass
            
            logger.info(f"[FontRegistry] {len(registry)} familles indexées")
        except Exception as e:
            logger.error(f"[FontRegistry] Erreur: {e}")
        
        self._font_registry_cache = registry
        return registry
    
    def get_text_font(self):
        """Récupère police via registre"""
        family = self.text_font_family.get()
        size = self.text_font_size.get()
        is_bold = self.text_bold.get() if hasattr(self, 'text_bold') else False
        is_italic = self.text_italic.get() if hasattr(self, 'text_italic') else False
        
        logger.info(f"[get_text_font] {family} {size}pt B={is_bold} I={is_italic}")
        
        registry = self._build_font_registry()
        styles = registry.get(family.lower())
        
        if styles:
            wanted = (is_bold, is_italic)
            
            # 1. Style exact
            if wanted in styles:
                fp = styles[wanted]
                try:
                    font = ImageFont.truetype(str(fp), size)
                    logger.info(f"  ✓ {fp.name}")
                    return font
                except Exception as e:
                    logger.warning(f"  ⚠ {fp.name}: {e}")
            
            # 2. Fallback prioritaire
            for sk in [(is_bold, False), (False, is_italic), (False, False)]:
                if sk in styles:
                    fp = styles[sk]
                    try:
                        font = ImageFont.truetype(str(fp), size)
                        logger.info(f"  ✓ {fp.name} (fallback)")
                        return font
                    except:
                        continue
            
            # 3. Premier disponible
            for fp in styles.values():
                try:
                    font = ImageFont.truetype(str(fp), size)
                    logger.info(f"  ✓ {fp.name} (1er dispo)")
                    return font
                except:
                    continue
        
        # PIL direct
        try:
            font = ImageFont.truetype(family, size)
            logger.info(f"  ✓ {family} (PIL)")
            return font
        except:
            pass
        
        # Fallback Arial
        logger.warning(f"  ⚠ {family} introuvable, Arial défaut")
        try:
            return ImageFont.truetype("arial.ttf", size)
        except:
            return ImageFont.load_default()

    def _get_usable_fonts(self):
        """Liste des polices réellement utilisables (présentes dans le registre)"""
        if hasattr(self, '_usable_fonts_cache'):
            return self._usable_fonts_cache
        
        registry = self._build_font_registry()
        
        if registry:
            # Familles avec capitalisation propre depuis registre
            # On reconstruit les noms avec leur casse originale
            try:
                import winreg
                key_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts"
                proper_names = {}  # {lower: ProperCase}
                
                for hive in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
                    try:
                        key = winreg.OpenKey(hive, key_path)
                    except (FileNotFoundError, OSError):
                        continue
                    
                    i = 0
                    while True:
                        try:
                            name, _, _ = winreg.EnumValue(key, i)
                            i += 1
                        except OSError:
                            break
                        
                        if not name:
                            continue
                        if '(TrueType)' not in name and '(OpenType)' not in name:
                            continue
                        
                        full_name = re.sub(r'\s*\((?:TrueType|OpenType)\)\s*$', '', name).strip()
                        
                        # Extraire famille (sans Bold/Italic)
                        family = full_name
                        for kw in ['Bold Italic', 'Gras Italique', 'Bold Oblique',
                                   'Bold', 'Gras', 'Italic', 'Italique', 'Oblique', 'Regular']:
                            family = re.sub(r'\s+' + re.escape(kw) + r'$', '', family, flags=re.IGNORECASE)
                        family = family.strip()
                        
                        fl = family.lower()
                        if fl in registry and fl not in proper_names:
                            proper_names[fl] = family
                    
                    try:
                        winreg.CloseKey(key)
                    except:
                        pass
                
                # Liste triée
                fonts = sorted(proper_names.values())
                logger.info(f"[FontList] {len(fonts)} polices utilisables")
                self._usable_fonts_cache = fonts
                return fonts
            except Exception as e:
                logger.warning(f"[FontList] Erreur: {e}")
        
        # Fallback: utiliser tkfont
        try:
            from tkinter import font as tkfont
            fonts = sorted([f for f in set(tkfont.families()) if f and not f.startswith('@')])
            self._usable_fonts_cache = fonts
            return fonts
        except Exception:
            return ['Arial', 'Times New Roman', 'Courier New']


if __name__ == "__main__":
    try:
        app = DMDConverter()
        app.run()
    except Exception as e:
        print(f"ERREUR FATALE: {e}")
        import traceback
        traceback.print_exc()