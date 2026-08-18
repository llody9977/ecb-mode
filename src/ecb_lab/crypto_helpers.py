"""AES helpers shared by the ECB weakness demonstrations.

ECB is used here intentionally, alongside CBC and GCM, to demonstrate the failure it
causes. Do not copy the ECB path into a system that needs confidentiality.
"""

from __future__ import annotations

import os

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

BLOCK_SIZE = 16


def pad_pkcs7(data: bytes, block_size: int = BLOCK_SIZE) -> bytes:
    """Pad data to a multiple of block_size using PKCS#7."""
    pad_len = block_size - (len(data) % block_size)
    return data + bytes([pad_len]) * pad_len


def unpad_pkcs7(data: bytes, block_size: int = BLOCK_SIZE) -> bytes:
    """Remove PKCS#7 padding. Raises ValueError if the padding is malformed."""
    if not data or len(data) % block_size != 0:
        raise ValueError("data length is not a multiple of the block size")
    pad_len = data[-1]
    if pad_len < 1 or pad_len > block_size or data[-pad_len:] != bytes([pad_len]) * pad_len:
        raise ValueError("invalid PKCS#7 padding")
    return data[:-pad_len]


def aes_ecb_encrypt(key: bytes, plaintext: bytes, pad: bool = True) -> bytes:
    """Encrypt with AES-ECB. Intentionally insecure — used only to demonstrate the failure."""
    if pad:
        plaintext = pad_pkcs7(plaintext)
    encryptor = Cipher(algorithms.AES(key), modes.ECB()).encryptor()  # nosec B305
    return encryptor.update(plaintext) + encryptor.finalize()


def aes_ecb_decrypt(key: bytes, ciphertext: bytes, unpad: bool = True) -> bytes:
    """Decrypt AES-ECB ciphertext produced by aes_ecb_encrypt."""
    decryptor = Cipher(algorithms.AES(key), modes.ECB()).decryptor()  # nosec B305
    plaintext = decryptor.update(ciphertext) + decryptor.finalize()
    return unpad_pkcs7(plaintext) if unpad else plaintext


def aes_cbc_encrypt(key: bytes, plaintext: bytes, iv: bytes | None = None) -> tuple[bytes, bytes]:
    """Encrypt with AES-CBC under a fresh random IV (generated if not supplied). Returns (iv, ciphertext)."""
    iv = iv if iv is not None else os.urandom(BLOCK_SIZE)
    encryptor = Cipher(algorithms.AES(key), modes.CBC(iv)).encryptor()
    ciphertext = encryptor.update(pad_pkcs7(plaintext)) + encryptor.finalize()
    return iv, ciphertext


def aes_cbc_decrypt(key: bytes, iv: bytes, ciphertext: bytes) -> bytes:
    """Decrypt AES-CBC ciphertext produced by aes_cbc_encrypt."""
    decryptor = Cipher(algorithms.AES(key), modes.CBC(iv)).decryptor()
    return unpad_pkcs7(decryptor.update(ciphertext) + decryptor.finalize())


def aes_gcm_encrypt(key: bytes, plaintext: bytes, associated_data: bytes = b"") -> tuple[bytes, bytes]:
    """Encrypt with AES-GCM under a fresh random 96-bit nonce. Returns (nonce, ciphertext_with_tag)."""
    nonce = os.urandom(12)
    ciphertext_with_tag = AESGCM(key).encrypt(nonce, plaintext, associated_data or None)
    return nonce, ciphertext_with_tag


def aes_gcm_decrypt(key: bytes, nonce: bytes, ciphertext_with_tag: bytes, associated_data: bytes = b"") -> bytes:
    """Decrypt and authenticate AES-GCM ciphertext. Raises cryptography.exceptions.InvalidTag on tampering."""
    return AESGCM(key).decrypt(nonce, ciphertext_with_tag, associated_data or None)


def split_blocks(data: bytes, block_size: int = BLOCK_SIZE) -> list[bytes]:
    """Split a byte string into fixed-size blocks (the final block may be short)."""
    return [data[i : i + block_size] for i in range(0, len(data), block_size)]
