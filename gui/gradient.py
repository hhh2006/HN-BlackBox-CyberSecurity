# -*- coding: utf-8 -*-
"""
gradient.py

Tkinter has no native gradient-fill support, so we render one ourselves
as a bitmap (numpy does the pixel math, PIL wraps it into an Image) and
use it as a full-window background. Every other widget on top uses a
transparent or coordinated solid fill, so the gradient reads as one
continuous background instead of a patchwork of colored boxes.
"""

import numpy as np
from PIL import Image
import customtkinter as ctk


def _hex_to_rgb(hex_color: str):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def build_gradient(width: int, height: int, stops, angle_deg: float = 135) -> Image.Image:
    colors = np.array([_hex_to_rgb(c) for c in stops], dtype=np.float32)
    n_stops = len(colors)

    y, x = np.mgrid[0:height, 0:width].astype(np.float32)
    angle_rad = np.deg2rad(angle_deg)
    proj = x * np.cos(angle_rad) + y * np.sin(angle_rad)
    proj -= proj.min()
    proj /= proj.max() if proj.max() > 0 else 1
    proj *= (n_stops - 1)

    idx_low = np.clip(proj.astype(int), 0, n_stops - 2)
    frac = (proj - idx_low)[..., None]

    rgb = colors[idx_low] * (1 - frac) + colors[idx_low + 1] * frac
    rgb = np.clip(rgb, 0, 255).astype(np.uint8)
    return Image.fromarray(rgb, mode="RGB")


def gradient_ctk_image(width: int, height: int, stops, angle_deg: float = 135) -> ctk.CTkImage:
    img = build_gradient(width, height, stops, angle_deg)
    return ctk.CTkImage(light_image=img, dark_image=img, size=(width, height))
