import os

from ecb_lab.detection import has_repeated_blocks
from ecb_lab.pattern_leakage import encrypt_image_under_each_mode, generate_sample_bitmap


def test_ecb_leaks_repeated_blocks_cbc_and_gcm_do_not():
    key = os.urandom(16)
    img = generate_sample_bitmap(width=64, height=64)  # small: fast test, still has uniform regions
    results = encrypt_image_under_each_mode(img, key)

    ecb_bytes = results["ecb"].tobytes()
    cbc_bytes = results["cbc"].tobytes()
    gcm_bytes = results["gcm"].tobytes()

    assert has_repeated_blocks(ecb_bytes) is True
    assert has_repeated_blocks(cbc_bytes) is False
    assert has_repeated_blocks(gcm_bytes) is False


def test_ecb_output_is_not_simply_identical_to_plaintext():
    key = os.urandom(16)
    img = generate_sample_bitmap(width=64, height=64)
    results = encrypt_image_under_each_mode(img, key)
    assert results["ecb"].tobytes() != img.tobytes()
