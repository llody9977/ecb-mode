from ecb_lab.oracle_attack import detect_block_size, make_suffix_oracle, recover_secret


def test_recovers_short_secret():
    secret = b"FLAG{ecb_leaks_everything}"
    oracle = make_suffix_oracle(secret)
    assert recover_secret(oracle) == secret


def test_recovers_secret_not_aligned_to_block_boundary():
    secret = b"x"  # 1 byte, well under one block
    oracle = make_suffix_oracle(secret)
    assert recover_secret(oracle) == secret


def test_recovers_secret_spanning_multiple_blocks():
    secret = b"A" * 5 + b"B" * 16 + b"C" * 9  # spans 3 blocks, not block-aligned
    oracle = make_suffix_oracle(secret)
    assert recover_secret(oracle) == secret


def test_detect_block_size_reports_16_for_aes():
    oracle = make_suffix_oracle(b"anything")
    assert detect_block_size(oracle) == 16


def test_recovers_secret_exactly_one_block_long():
    # PKCS#7 always adds a full padding block when data is already block-aligned, so a
    # 16-byte secret is the edge case where the empty-input ciphertext is a full block
    # longer than the secret itself -- worth its own test, not just analysis.
    secret = b"B" * 16
    oracle = make_suffix_oracle(secret)
    assert recover_secret(oracle) == secret


def test_recovers_secret_exactly_two_blocks_long():
    secret = b"C" * 32
    oracle = make_suffix_oracle(secret)
    assert recover_secret(oracle) == secret
