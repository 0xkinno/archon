"""
Cryptographic Evidence Signing for ARCHON Incident State and Audit Manifests.

Provides deterministic Ed25519 / HMAC-SHA256 signature generation and verification.
Can utilize Google Cloud KMS asymmetric signing keys or local Ed25519 keypairs.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Tuple

# Try cryptography library, fallback to HMAC if not present
try:
    from cryptography.hazmat.primitives.asymmetric import ed25519
    from cryptography.hazmat.primitives import serialization
    HAS_ED25519 = True
except ImportError:
    HAS_ED25519 = False


SECRETS_DIR = Path(__file__).resolve().parent.parent / "secrets"
PRIVATE_KEY_PATH = SECRETS_DIR / "evidence-signer.key"
PUBLIC_KEY_PATH = SECRETS_DIR / "evidence-signer.pub.pem"


def canonical_json(data: Any) -> bytes:
    """Serialize data structure to deterministic canonical JSON bytes."""
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def compute_state_hash(state_dict: dict[str, Any]) -> str:
    """Compute SHA-256 hex digest over canonicalized state."""
    clean_state = {k: v for k, v in state_dict.items() if k not in ("signature", "signature_type", "public_key", "state_hash")}
    return hashlib.sha256(canonical_json(clean_state)).hexdigest()


def ensure_keypair() -> Tuple[str, str]:
    """Ensure Ed25519 keypair exists in secrets dir or generate one."""
    SECRETS_DIR.mkdir(parents=True, exist_ok=True)

    if HAS_ED25519:
        if PRIVATE_KEY_PATH.exists() and PUBLIC_KEY_PATH.exists():
            priv_bytes = PRIVATE_KEY_PATH.read_bytes()
            pub_pem = PUBLIC_KEY_PATH.read_text(encoding="utf-8")
            return base64.b64encode(priv_bytes).decode("ascii"), pub_pem

        private_key = ed25519.Ed25519PrivateKey.generate()
        public_key = private_key.public_key()

        priv_raw = private_key.private_bytes_raw()
        pub_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode("utf-8")

        PRIVATE_KEY_PATH.write_bytes(priv_raw)
        PUBLIC_KEY_PATH.write_text(pub_pem, encoding="utf-8")
        return base64.b64encode(priv_raw).decode("ascii"), pub_pem
    else:
        # Fallback secret for HMAC if cryptography is not installed
        secret_path = SECRETS_DIR / "evidence-hmac.key"
        if not secret_path.exists():
            secret = hashlib.sha256(os.urandom(32)).hexdigest()
            secret_path.write_text(secret, encoding="utf-8")
        else:
            secret = secret_path.read_text(encoding="utf-8").strip()
        return secret, "HMAC-SHA256"


def sign_incident_state(state_dict: dict[str, Any]) -> dict[str, Any]:
    """
    Sign incident state hash and return signature metadata.
    """
    state_hash = compute_state_hash(state_dict)
    priv_key_str, pub_pem = ensure_keypair()

    if HAS_ED25519 and pub_pem.startswith("-----BEGIN PUBLIC KEY-----"):
        priv_bytes = base64.b64decode(priv_key_str)
        priv_key = ed25519.Ed25519PrivateKey.from_private_bytes(priv_bytes)
        signature = priv_key.sign(state_hash.encode("utf-8"))
        sig_b64 = base64.b64encode(signature).decode("ascii")
        sig_type = "ED25519"
    else:
        import hmac
        sig_bytes = hmac.new(priv_key_str.encode("utf-8"), state_hash.encode("utf-8"), hashlib.sha256).digest()
        sig_b64 = base64.b64encode(sig_bytes).decode("ascii")
        sig_type = "HMAC-SHA256"

    return {
        "state_hash": state_hash,
        "signature": sig_b64,
        "signature_type": sig_type,
        "public_key": pub_pem if sig_type == "ED25519" else "LOCAL-SECRET",
    }


def verify_incident_signature(state_dict: dict[str, Any], signature_b64: str, public_key_pem: str, sig_type: str = "ED25519") -> bool:
    """
    Verify cryptographic signature against state hash.
    """
    if not signature_b64:
        return False

    state_hash = compute_state_hash(state_dict)

    try:
        if HAS_ED25519 and sig_type == "ED25519" and public_key_pem and public_key_pem.startswith("-----BEGIN"):
            pub_key = serialization.load_pem_public_key(public_key_pem.encode("utf-8"))
            if isinstance(pub_key, ed25519.Ed25519PublicKey):
                sig_bytes = base64.b64decode(signature_b64)
                pub_key.verify(sig_bytes, state_hash.encode("utf-8"))
                return True
        elif sig_type == "HMAC-SHA256":
            import hmac
            secret_path = SECRETS_DIR / "evidence-hmac.key"
            if secret_path.exists():
                secret = secret_path.read_text(encoding="utf-8").strip()
                expected = base64.b64encode(
                    hmac.new(secret.encode("utf-8"), state_hash.encode("utf-8"), hashlib.sha256).digest()
                ).decode("ascii")
                return hmac.compare_digest(expected, signature_b64)
    except Exception:
        return False

    return False
