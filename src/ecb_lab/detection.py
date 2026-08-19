"""Detecting AES-ECB usage, black-box and white-box.

Black-box: given only ciphertext, exploit the property under test (identical plaintext
blocks -> identical ciphertext blocks) to flag ECB with no key and no source access.

White-box: ECB is frequently not a deliberate choice. Several mainstream crypto libraries
fall back to ECB when a caller specifies only the cipher name, so a static-analysis pass
over source/config is often more informative than probing ciphertext.
"""

from __future__ import annotations

from dataclasses import dataclass

from .crypto_helpers import BLOCK_SIZE, split_blocks


def has_repeated_blocks(ciphertext: bytes, block_size: int = BLOCK_SIZE) -> bool:
    """True if any two blocks in this single ciphertext are identical.

    This is sufficient evidence of deterministic, block-independent encryption -- of
    which ECB is the overwhelmingly likely real-world cause, though not the only
    logically possible one -- but it is not a necessary condition: it only fires when
    the plaintext itself happened to contain two identical blocks (e.g. padding,
    repeated headers, uniform image regions). ECB ciphertext without any repeated
    plaintext block looks like any other block cipher's output under this test alone.
    """
    blocks = split_blocks(ciphertext, block_size)
    return len(blocks) != len(set(blocks))


def likely_ecb_encryptor(encrypt_fn, block_size: int = BLOCK_SIZE, probe_blocks: int = 3) -> bool:
    """Actively probe a black-box encryption oracle for ECB behavior.

    Feeds `probe_blocks` identical plaintext blocks through `encrypt_fn` (any callable
    bytes -> bytes) and checks for repeated ciphertext blocks in the response. Unlike
    `has_repeated_blocks`, this does not depend on the *target's own* plaintext
    containing a repeat — the caller supplies the repeat. This is the technique behind
    Cryptopals Set 1 Challenge 8 ("Detect AES in ECB mode") and the ECB pre-check in
    Set 2 Challenge 12's byte-at-a-time oracle attack.
    """
    probe = b"A" * block_size * probe_blocks
    return has_repeated_blocks(encrypt_fn(probe), block_size)


@dataclass(frozen=True)
class StaticFinding:
    library: str
    trigger: str
    real_world_instance: str


# White-box signal: libraries and APIs that produce ECB either by explicit request or by
# silent default when the caller under-specifies the cipher mode. Verified against each
# vendor's own documentation / advisory, not inferred.
KNOWN_ECB_DEFAULT_FOOTGUNS: list[StaticFinding] = [
    StaticFinding(
        library="Java Cipher (JCA)",
        trigger='Cipher.getInstance("AES") with no mode/padding suffix silently resolves to '
        '"AES/ECB/PKCS5Padding".',
        real_world_instance="Reported in production apps including MEGA (github.com/meganz/android#299), "
        "bilibili's Android client (github.com/10miaomiao/bilimiao2#270), and India's Aarogya Setu "
        "COVID contact-tracing app (github.com/nic-delhi/AarogyaSetu_Android#203).",
    ),
    StaticFinding(
        library="BouncyCastle (as used from Android apps)",
        trigger="Callers that request only a block cipher name (e.g. `AES`, `DES`) without an explicit "
        "mode get ECB from BouncyCastle's provider.",
        real_world_instance="Egele, Brumley, Fratantonio & Kruegel, 'An Empirical Study of Cryptographic "
        "Misuse in Android Applications' (ACM CCS 2013): of 11,748 apps using crypto APIs, 7,656 violated "
        "the 'do not use ECB' rule at least once; 5,656 of those came from BouncyCastle's ECB-by-default "
        "behavior when only a block cipher was specified.",
    ),
]

# grep-able source signatures for a quick static pass over a codebase.
STATIC_GREP_PATTERNS: tuple[str, ...] = (
    r"MODE_ECB",  # PyCryptodome / PyCrypto
    r"modes\.ECB\(",  # pyca/cryptography
    r"/ECB/",  # Java-style transformation strings, e.g. AES/ECB/PKCS5Padding
    r'Cipher\.getInstance\(\s*"AES"\s*\)',  # Java default-mode footgun (resolves to ECB)
    r"AES\.new\(\s*[\w.\[\]'\"]+\s*,\s*AES\.MODE_ECB",  # PyCryptodome explicit ECB construction
)
