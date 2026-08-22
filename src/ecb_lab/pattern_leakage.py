"""Vector 1: pattern and structure leakage.

ECB's determinism means identical plaintext regions become identical ciphertext regions.
Encrypting a structured bitmap makes this visible without any statistical analysis: the
outline of the source image survives into the ciphertext.
"""

from __future__ import annotations

from PIL import Image, ImageDraw

from .crypto_helpers import aes_cbc_encrypt, aes_ecb_encrypt, aes_gcm_encrypt


def generate_sample_bitmap(width: int = 256, height: int = 256) -> Image.Image:
    """A synthetic structured RGB image with large uniform regions, deliberately not the
    copyrighted 'Tux' image used in the well-known original demonstration."""
    img = Image.new("RGB", (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.ellipse([20, 20, width - 20, height - 20], fill=(15, 45, 90), outline=(200, 40, 40), width=6)
    draw.rectangle([width // 2 - 40, height // 2 - 60, width // 2 + 40, height // 2 + 60], fill=(230, 230, 230))
    draw.polygon(
        [(width // 2, 40), (width - 60, height // 2), (width // 2, height - 40), (60, height // 2)],
        outline=(200, 40, 40),
        width=4,
    )
    return img


def encrypt_image_under_each_mode(img: Image.Image, key: bytes) -> dict[str, Image.Image]:
    """Encrypt raw pixel bytes under ECB, CBC, and GCM, and rebuild each result as an image
    of the same dimensions so the difference is visible directly."""
    width, height = img.size
    raw = img.tobytes()

    ecb_ct = aes_ecb_encrypt(key, raw, pad=True)[: len(raw)]
    _iv, cbc_ct = aes_cbc_encrypt(key, raw)
    cbc_ct = cbc_ct[: len(raw)]
    _nonce, gcm_ct = aes_gcm_encrypt(key, raw)
    gcm_ct = gcm_ct[: len(raw)]

    return {
        "original": img,
        "ecb": Image.frombytes("RGB", (width, height), ecb_ct),
        "cbc": Image.frombytes("RGB", (width, height), cbc_ct),
        "gcm": Image.frombytes("RGB", (width, height), gcm_ct),
    }
