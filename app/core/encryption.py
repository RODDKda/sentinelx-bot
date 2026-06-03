"""AES-256-GCM encryption for private key storage.

Security model:
  - Master key from ENCRYPTION_KEY env var (64 hex chars = 32 bytes)
  - HKDF-SHA256 derives per-encryption key using random salt
  - AES-256-GCM with user_id as AAD (binds ciphertext to user)
  - Salt, IV, and Tag stored alongside ciphertext
"""

import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes


class KeyEncryption:
    """AES-256-GCM private key encryption with HKDF key derivation."""

    SALT_LENGTH = 16
    IV_LENGTH = 12
    TAG_LENGTH = 16  # GCM tag is 16 bytes
    HKDF_INFO = b"sentinelx-key-encryption-v1"

    def __init__(self, master_key: str):
        """
        Initialize with hex-encoded master key.

        Args:
            master_key: 64-character hex string (32 bytes)
        """
        self.master_key = bytes.fromhex(master_key)
        if len(self.master_key) != 32:
            raise ValueError(f"Master key must be 32 bytes (64 hex chars), got {len(self.master_key)}")

    def encrypt(self, plaintext: str, user_id: str) -> dict:
        """
        Encrypt plaintext with AES-256-GCM.

        Args:
            plaintext: The private key to encrypt
            user_id: User ID used as AAD (binds ciphertext to user)

        Returns:
            dict with keys: ciphertext (bytes), salt (bytes), iv (bytes), tag (bytes)
        """
        salt = os.urandom(self.SALT_LENGTH)
        iv = os.urandom(self.IV_LENGTH)

        # Derive encryption key via HKDF
        derived_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            info=self.HKDF_INFO,
        ).derive(self.master_key)

        # Encrypt
        aesgcm = AESGCM(derived_key)
        data = plaintext.encode("utf-8")
        aad = user_id.encode("utf-8")
        ciphertext_with_tag = aesgcm.encrypt(nonce=iv, data=data, associated_data=aad)

        # Split ciphertext and tag (tag is last 16 bytes in GCM)
        tag = ciphertext_with_tag[-self.TAG_LENGTH:]
        ciphertext = ciphertext_with_tag[:-self.TAG_LENGTH]

        return {
            "ciphertext": ciphertext,
            "salt": salt,
            "iv": iv,
            "tag": tag,
        }

    def decrypt(self, ciphertext: bytes, salt: bytes, iv: bytes, tag: bytes, user_id: str) -> str:
        """
        Decrypt ciphertext with AES-256-GCM.

        Args:
            ciphertext: Encrypted data
            salt: HKDF salt
            iv: AES-GCM initialization vector
            tag: GCM authentication tag
            user_id: User ID for AAD verification

        Returns:
            Decrypted plaintext string

        Raises:
            InvalidTag: If decryption fails (wrong key or tampered data)
        """
        derived_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            info=self.HKDF_INFO,
        ).derive(self.master_key)

        aesgcm = AESGCM(derived_key)
        aad = user_id.encode("utf-8")
        plaintext = aesgcm.decrypt(nonce=iv, data=ciphertext + tag, associated_data=aad)

        return plaintext.decode("utf-8")
