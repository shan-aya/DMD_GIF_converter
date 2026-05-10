import hashlib

import numpy as np
from PIL import Image

try:
    from .dmd_engine import DMDEngine
except ImportError:
    from dmd_engine import DMDEngine


def hash_image(img: Image.Image) -> str:
    """Retourne un hash stable pour une image RGB."""
    data = img.convert("RGB").tobytes()
    return hashlib.md5(data).hexdigest()


def evaluate_quality(
    original_img: Image.Image,
    dmd_canvas: Image.Image,
    settings=None,
    pixel_perfect: bool = False,
) -> float:
    """Évalue la qualité d'une conversion (score bas = meilleur).

    Dépendance au contexte: le score privilégie la lisibilité DMD
    (contraste/contours/occupation) et non la simple similarité pixel-wise.
    """
    if settings is None:
        # Mode legacy: comparaison pixel-wise simple
        resample = (
            Image.Resampling.NEAREST if pixel_perfect else Image.Resampling.LANCZOS
        )
        reference = original_img.convert("RGB").resize((128, 32), resample)
        arr_orig = np.array(reference).astype(float)
        arr_dmd = np.array(dmd_canvas.convert("RGB")).astype(float)
        diff = np.mean(np.abs(arr_orig - arr_dmd))
        white_orig = np.sum(np.all(arr_orig > 240, axis=2))
        white_dmd = np.sum(np.all(arr_dmd > 240, axis=2))
        white_penalty = max(0, white_dmd - white_orig) * 5
        return diff + white_penalty

    img = original_img.convert("RGB")
    resample = Image.Resampling.NEAREST if pixel_perfect else Image.Resampling.LANCZOS

    optimized = DMDEngine.optimize_for_dmd(img, settings)
    resized, new_w, new_h = DMDEngine.adaptive_resize(
        optimized,
        128,
        32,
        settings["resize_mode"],
        pixel_perfect=pixel_perfect,
    )

    # On évalue sur plusieurs frames pour que le mode scrolling puisse être valorisé
    dmd_frames, _ = DMDEngine.create_animation_frames(
        resized,
        settings,
        (0, 0, 0),
        cleanup=False,
        cleanup_power=settings.get("cleanup_power", 1.0),
    )

    # échantillonner quelques frames plutôt que seulement [0]
    if len(dmd_frames) <= 3:
        dmd_sample = dmd_frames
    else:
        idxs = [
            0,
            len(dmd_frames) // 3,
            (2 * len(dmd_frames)) // 3,
            len(dmd_frames) - 1,
        ]
        seen = set()
        dmd_sample = []
        for i in idxs:
            if i not in seen and 0 <= i < len(dmd_frames):
                dmd_sample.append(dmd_frames[i])
                seen.add(i)

    # Frame de référence pour la comparaison (modèle)
    dmd_frame0 = dmd_sample[0].convert("RGB")

    ref_resized = img.resize((new_w, new_h), resample)
    ref_frames, _ = DMDEngine.create_animation_frames(
        ref_resized,
        settings,
        (0, 0, 0),
        cleanup=False,
        cleanup_power=0.0,
    )
    ref_frame0 = ref_frames[0].convert("RGB")

    def rgb_to_luma(arr_rgb: np.ndarray) -> np.ndarray:
        r = arr_rgb[:, :, 0]
        g = arr_rgb[:, :, 1]
        b = arr_rgb[:, :, 2]
        return 0.299 * r + 0.587 * g + 0.114 * b

    l_ref = rgb_to_luma(np.array(ref_frame0).astype(np.float32))
    l_cand = rgb_to_luma(np.array(dmd_frame0).astype(np.float32))

    def estimate_bg_luma(luma: np.ndarray) -> float:
        h, w = luma.shape
        cs = min(6, max(1, min(h, w) // 8))
        corners = np.concatenate(
            [
                luma[:cs, :cs].reshape(-1),
                luma[:cs, -cs:].reshape(-1),
                luma[-cs:, :cs].reshape(-1),
                luma[-cs:, -cs:].reshape(-1),
            ]
        )
        return float(np.median(corners))

    bg_ref = estimate_bg_luma(l_ref)
    bg_cand = estimate_bg_luma(l_cand)

    thr_ref = bg_ref + 18.0
    thr_cand = bg_cand + 18.0

    active_ref = float(np.mean(l_ref > thr_ref))
    active_cand = float(np.mean(l_cand > thr_cand))

    # Occupation: pénaliser images trop petites/peu actives
    target_low, target_high = 0.08, 0.25
    occ_pen = 0.0
    if active_cand < target_low:
        occ_pen = (target_low - active_cand) * 25.0
    elif active_cand > target_high:
        occ_pen = (active_cand - target_high) * 8.0

    # Contraste local sur les pixels actifs
    def local_contrast(luma: np.ndarray, thr: float) -> float:
        mask = luma > thr
        if int(mask.sum()) < 8:
            return 0.0
        vals = luma[mask]
        return float(np.std(vals))

    cont_ref = local_contrast(l_ref, thr_ref)
    cont_cand = local_contrast(l_cand, thr_cand)
    cont_pen = abs(cont_ref - cont_cand) / 50.0

    # Contours: gradient magnitude (Sobel approximé)
    def sobel_mag(luma: np.ndarray) -> np.ndarray:
        kx = np.array([[1, 0, -1], [2, 0, -2], [1, 0, -1]], dtype=np.float32)
        ky = np.array([[1, 2, 1], [0, 0, 0], [-1, -2, -1]], dtype=np.float32)
        pad = 1
        L = np.pad(luma, ((pad, pad), (pad, pad)), mode="edge")

        gx = (
            kx[0, 0] * L[:-2, :-2]
            + kx[0, 1] * L[:-2, 1:-1]
            + kx[0, 2] * L[:-2, 2:]
            + kx[1, 0] * L[1:-1, :-2]
            + kx[1, 1] * L[1:-1, 1:-1]
            + kx[1, 2] * L[1:-1, 2:]
            + kx[2, 0] * L[2:, :-2]
            + kx[2, 1] * L[2:, 1:-1]
            + kx[2, 2] * L[2:, 2:]
        )
        gy = (
            ky[0, 0] * L[:-2, :-2]
            + ky[0, 1] * L[:-2, 1:-1]
            + ky[0, 2] * L[:-2, 2:]
            + ky[1, 0] * L[1:-1, :-2]
            + ky[1, 1] * L[1:-1, 1:-1]
            + ky[1, 2] * L[1:-1, 2:]
            + ky[2, 0] * L[2:, :-2]
            + ky[2, 1] * L[2:, 1:-1]
            + ky[2, 2] * L[2:, 2:]
        )
        return np.sqrt(gx * gx + gy * gy)

    g_ref = sobel_mag(l_ref)
    g_cand = sobel_mag(l_cand)

    mask_edges = (g_ref > 20) | (g_cand > 20)
    if int(mask_edges.sum()) < 16:
        edge_diff = float(np.mean(np.abs(g_ref - g_cand)))
    else:
        edge_diff = float(np.mean(np.abs(g_ref[mask_edges] - g_cand[mask_edges])))

    # Fidélité (composante faible, pour ne pas trop “détruire” la ressemblance)
    luma_diff = float(np.mean(np.abs(l_ref - l_cand)))

    white_orig = float(np.sum(l_ref > 240.0))
    white_cand = float(np.sum(l_cand > 240.0))
    white_penalty = max(0.0, white_cand - white_orig) / (128 * 32)

    # Bonus explicite anti-“trop petit”
    small_pen = 0.0
    if active_ref > target_low and active_cand < 0.03:
        small_pen = (0.03 - active_cand) * 80.0

    # =============================
    # LISIBILITÉ TEXTE / LOGO
    # =============================
    def active_edge_strength(luma: np.ndarray, thr: float) -> float:
        mask = luma > thr
        if int(mask.sum()) < 8:
            return 0.0

        kx = np.array([[1, 0, -1], [2, 0, -2], [1, 0, -1]], dtype=np.float32)
        ky = np.array([[1, 2, 1], [0, 0, 0], [-1, -2, -1]], dtype=np.float32)
        pad = 1
        L = np.pad(luma, ((pad, pad), (pad, pad)), mode="edge")
        gx = (
            kx[0, 0] * L[:-2, :-2]
            + kx[0, 1] * L[:-2, 1:-1]
            + kx[0, 2] * L[:-2, 2:]
            + kx[1, 0] * L[1:-1, :-2]
            + kx[1, 1] * L[1:-1, 1:-1]
            + kx[1, 2] * L[1:-1, 2:]
            + kx[2, 0] * L[2:, :-2]
            + kx[2, 1] * L[2:, 1:-1]
            + kx[2, 2] * L[2:, 2:]
        )
        gy = (
            ky[0, 0] * L[:-2, :-2]
            + ky[0, 1] * L[:-2, 1:-1]
            + ky[0, 2] * L[:-2, 2:]
            + ky[1, 0] * L[1:-1, :-2]
            + ky[1, 1] * L[1:-1, 1:-1]
            + ky[1, 2] * L[1:-1, 2:]
            + ky[2, 0] * L[2:, :-2]
            + ky[2, 1] * L[2:, 1:-1]
            + ky[2, 2] * L[2:, 2:]
        )
        gmag = np.sqrt(gx * gx + gy * gy)
        vals = gmag[mask]
        return float(np.mean(vals)) if vals.size else 0.0

    edge_strength_ref = active_edge_strength(l_ref, thr_ref)
    edge_strength_cand = active_edge_strength(l_cand, thr_cand)

    lis_pen = 0.0
    if edge_strength_ref > 0:
        if edge_strength_cand < edge_strength_ref:
            lis_pen = (
                (edge_strength_ref - edge_strength_cand)
                / max(1.0, edge_strength_ref)
                * 1.8
            )
        else:
            lis_pen = (
                (edge_strength_cand - edge_strength_ref)
                / max(1.0, edge_strength_ref)
                * 0.2
            )

    # =============================
    # POIDS - priorité lisibilité
    # =============================
    w_fid = 0.25
    w_edge = 0.95
    w_cont = 0.75
    w_occ = 1.25
    w_white = 0.55
    w_lis = 3.00

    score = (
        w_fid * luma_diff
        + w_edge * (edge_diff / 30.0)
        + w_cont * cont_pen
        + w_occ * occ_pen
        + w_white * white_penalty
        + w_lis * lis_pen
        + small_pen
    )

    return float(score)


def render_dmd_frame(
    image_path: str,
    settings: dict,
    return_frames: bool = False,
    cleanup: bool = True,
    cleanup_power: float = 1.0,
    pixel_perfect: bool = False,
):
    """Rend une image en DMD avec les paramètres donnés."""
    img_orig = Image.open(image_path)

    # Détecter fond
    bg_color, _is_dark = DMDEngine.detect_background_color(img_orig)

    # Forcer fond noir en mode AUTO pour conserver le rendu DMD attendu
    if settings.get("resize_mode") == "auto":
        bg_color = (0, 0, 0)

    # Optimiser pour DMD
    img = DMDEngine.optimize_for_dmd(img_orig, settings)

    # Redimensionner adaptatif
    img, new_w, new_h = DMDEngine.adaptive_resize(
        img,
        128,
        32,
        settings["resize_mode"],
        pixel_perfect=pixel_perfect,
    )

    if not return_frames:
        frames, _direction = DMDEngine.create_animation_frames(
            img,
            settings,
            bg_color,
            cleanup=(cleanup and settings.get("resize_mode") == "auto"),
            cleanup_power=cleanup_power,
        )
        return frames[0], settings["fps"]

    frames, _direction = DMDEngine.create_animation_frames(
        img,
        settings,
        bg_color,
        cleanup=(cleanup and settings.get("resize_mode") == "auto"),
        cleanup_power=cleanup_power,
    )
    return frames, settings["fps"]
