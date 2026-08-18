"""Vector 3: chosen-plaintext byte-at-a-time secret recovery.

A vulnerable endpoint that computes AES-ECB(attacker_input || secret, key) leaks the
secret one byte per ~256 oracle queries, entirely from ciphertext -- the key is never
needed. This is Cryptopals Set 2 Challenge 12.
"""

from __future__ import annotations

import os
from typing import Callable

from .crypto_helpers import aes_ecb_encrypt, split_blocks
from .detection import likely_ecb_encryptor

Oracle = Callable[[bytes], bytes]


def make_suffix_oracle(secret: bytes, key: bytes | None = None) -> Oracle:
    """Build AES-ECB(attacker_input || secret, key) as a black-box callable."""
    key = key if key is not None else os.urandom(16)
    return lambda attacker_input: aes_ecb_encrypt(key, attacker_input + secret)


def detect_block_size(oracle: Oracle, max_probe: int = 64) -> int:
    """Find the cipher's block size by growing the input until the ciphertext length jumps."""
    base_len = len(oracle(b""))
    for i in range(1, max_probe):
        if len(oracle(b"A" * i)) > base_len:
            return len(oracle(b"A" * i)) - base_len
    raise ValueError("could not detect block size within max_probe bytes")


def _detect_secret_length(oracle: Oracle, block_size: int) -> int:
    """The padded ciphertext length grows by exactly one block once enough filler bytes
    push the PKCS#7 padding into a new block; the filler count at that point tells us
    exactly how many bytes of real padding the empty-input ciphertext already contained."""
    base_len = len(oracle(b""))
    for filler in range(1, block_size + 1):
        if len(oracle(b"A" * filler)) > base_len:
            return base_len - filler
    raise ValueError("could not determine secret length within one block of filler")


def recover_secret(oracle: Oracle, block_size: int | None = None) -> bytes:
    """Recover the oracle's fixed secret suffix one byte at a time.

    Requires the oracle to be ECB (checked via `likely_ecb_encryptor`) and to append the
    secret after unmodified attacker input, with no random prefix.
    """
    block_size = block_size if block_size is not None else detect_block_size(oracle)
    if not likely_ecb_encryptor(oracle, block_size):
        raise ValueError("oracle does not behave like ECB — this technique does not apply")

    secret_length = _detect_secret_length(oracle, block_size)
    recovered = bytearray()

    for byte_index in range(secret_length):
        pad_len = (-byte_index - 1) % block_size
        block_index = (byte_index + pad_len) // block_size
        target_block = split_blocks(oracle(b"A" * pad_len))[block_index]

        found = None
        for candidate in range(256):
            probe = b"A" * pad_len + bytes(recovered) + bytes([candidate])
            if split_blocks(oracle(probe))[block_index] == target_block:
                found = candidate
                break

        if found is None:
            raise RuntimeError(f"no candidate matched at byte {byte_index} — oracle behaved unexpectedly")
        recovered.append(found)

    return bytes(recovered)
