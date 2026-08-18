import os
import re

from ecb_lab.crypto_helpers import aes_cbc_encrypt, aes_ecb_encrypt
from ecb_lab.detection import (
    STATIC_GREP_PATTERNS,
    has_repeated_blocks,
    likely_ecb_encryptor,
)


def test_has_repeated_blocks_flags_ecb_with_repeated_plaintext():
    key = os.urandom(16)
    ciphertext = aes_ecb_encrypt(key, b"SAMEBLOCK1234567" * 0 + b"AAAAAAAAAAAAAAAA" * 2)
    assert has_repeated_blocks(ciphertext) is True


def test_has_repeated_blocks_is_silent_on_cbc_with_repeated_plaintext():
    key = os.urandom(16)
    _iv, ciphertext = aes_cbc_encrypt(key, b"AAAAAAAAAAAAAAAA" * 2)
    assert has_repeated_blocks(ciphertext) is False


def test_likely_ecb_encryptor_detects_ecb_oracle():
    key = os.urandom(16)
    assert likely_ecb_encryptor(lambda pt: aes_ecb_encrypt(key, pt)) is True


def test_likely_ecb_encryptor_rejects_cbc_oracle():
    key = os.urandom(16)
    assert likely_ecb_encryptor(lambda pt: aes_cbc_encrypt(key, pt)[1]) is False


def test_static_grep_patterns_match_known_footguns():
    samples = {
        r"MODE_ECB": "cipher = AES.new(key, AES.MODE_ECB)",
        r"modes\.ECB\(": "Cipher(algorithms.AES(key), modes.ECB())",
        r"/ECB/": 'Cipher.getInstance("AES/ECB/PKCS5Padding")',
        r'Cipher\.getInstance\(\s*"AES"\s*\)': 'Cipher.getInstance("AES")',
        r"AES\.new\(\s*\w+\s*,\s*AES\.MODE_ECB": "AES.new(key, AES.MODE_ECB)",
    }
    for pattern, sample in samples.items():
        assert pattern in STATIC_GREP_PATTERNS
        assert re.search(pattern, sample), f"pattern {pattern!r} should match {sample!r}"
