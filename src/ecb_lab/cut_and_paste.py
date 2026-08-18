"""Vector 4: block malleability -- cut-and-paste privilege escalation.

ECB blocks are independent and unauthenticated. If an attacker can get chosen plaintext
encrypted (e.g. by controlling the email field of their own account), they can splice
ciphertext blocks from one encryption into another and the server will decrypt and act on
the forged combination without any integrity check catching it. This is Cryptopals Set 2
Challenge 13.

Note: the profile string is built directly (not via urllib.parse.urlencode), because
percent-encoding would rewrite the raw PKCS#7 padding bytes injected below into multi-
character escape sequences and break the block alignment the attack depends on.
"""

from __future__ import annotations

import os

from .crypto_helpers import BLOCK_SIZE, aes_ecb_decrypt, aes_ecb_encrypt, split_blocks


class ProfileService:
    """A minimal stand-in for a backend that issues an encrypted session token encoding
    a user's role, and trusts whatever role the decrypted token names."""

    def __init__(self, key: bytes | None = None):
        self.key = key if key is not None else os.urandom(16)

    def issue_token(self, email: str) -> bytes:
        sanitized = email.replace("&", "").replace("=", "")
        profile = f"email={sanitized}&uid=1000&role=user"
        return aes_ecb_encrypt(self.key, profile.encode("latin1"))

    def role_for_token(self, token: bytes) -> str | None:
        try:
            plaintext = aes_ecb_decrypt(self.key, token)
        except ValueError:
            return None  # padding didn't validate — not a token this service issued
        fields = dict(
            pair.split("=", 1) for pair in plaintext.decode("latin1", errors="replace").split("&") if "=" in pair
        )
        return fields.get("role")


def forge_admin_token(service: ProfileService) -> bytes:
    """Splice a legitimate token into one that decrypts with role=admin, using only the
    public issue_token() interface -- no access to `service.key`."""
    # "email=" is 6 bytes; a 10-byte local part pushes the next byte to a block boundary,
    # so an "admin"+PKCS#7-padding block (16 bytes) lands isolated as ciphertext block 1.
    pad_byte = BLOCK_SIZE - len("admin")
    admin_block_plaintext = b"admin" + bytes([pad_byte]) * pad_byte
    donor_token = service.issue_token("x" * 10 + admin_block_plaintext.decode("latin1"))
    admin_block = split_blocks(donor_token)[1]

    # "email=" (6) + email + "&uid=1000&role=" (15) must land exactly on a block boundary
    # so that "user" + its padding is isolated in its own trailing block, safe to drop.
    prefix_len = len("email=") + len("&uid=1000&role=")
    email_len = (-prefix_len) % BLOCK_SIZE or BLOCK_SIZE
    base_token = service.issue_token("a" * email_len)
    base_blocks = split_blocks(base_token)[:-1]  # drop the trailing "user"+padding block

    return b"".join(base_blocks) + admin_block
