import os

import pytest
from cryptography.exceptions import InvalidTag

from ecb_lab.crypto_helpers import (
    aes_cbc_decrypt,
    aes_cbc_encrypt,
    aes_ecb_decrypt,
    aes_ecb_encrypt,
    aes_gcm_decrypt,
    aes_gcm_encrypt,
    pad_pkcs7,
    split_blocks,
    unpad_pkcs7,
)


def test_pkcs7_round_trip():
    for length in range(0, 40):
        data = os.urandom(length)
        assert unpad_pkcs7(pad_pkcs7(data)) == data


def test_pkcs7_rejects_bad_padding():
    with pytest.raises(ValueError):
        unpad_pkcs7(b"\x00" * 16)


def test_ecb_round_trip_and_determinism():
    key = os.urandom(16)
    plaintext = b"REPEATEDBLOCK!!!" * 2
    ciphertext = aes_ecb_encrypt(key, plaintext)
    assert aes_ecb_decrypt(key, ciphertext) == plaintext
    blocks = split_blocks(ciphertext)
    assert blocks[0] == blocks[1], "identical plaintext blocks must yield identical ciphertext blocks under ECB"


def test_cbc_round_trip_and_non_determinism():
    key = os.urandom(16)
    plaintext = b"REPEATEDBLOCK!!!" * 2
    iv1, ct1 = aes_cbc_encrypt(key, plaintext)
    iv2, ct2 = aes_cbc_encrypt(key, plaintext)
    assert aes_cbc_decrypt(key, iv1, ct1) == plaintext
    assert ct1 != ct2, "a fresh random IV must change the ciphertext for identical plaintext"
    assert split_blocks(ct1)[0] != split_blocks(ct1)[1], "CBC must not repeat blocks for repeated plaintext"


def test_gcm_round_trip_and_tamper_detection():
    key = os.urandom(32)
    plaintext = b"authenticated data stays authentic"
    nonce, ct = aes_gcm_encrypt(key, plaintext, associated_data=b"header")
    assert aes_gcm_decrypt(key, nonce, ct, associated_data=b"header") == plaintext

    tampered = bytearray(ct)
    tampered[0] ^= 0xFF
    with pytest.raises(InvalidTag):
        aes_gcm_decrypt(key, nonce, bytes(tampered), associated_data=b"header")
