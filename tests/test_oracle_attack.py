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
