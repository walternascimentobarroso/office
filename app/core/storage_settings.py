"""Object storage (local filesystem or S3-compatible) settings."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv

load_dotenv()

StorageBackend = Literal["local", "s3"]


@dataclass(frozen=True)
class StorageSettings:
    """Connection and paths for asset invoice uploads."""

    backend: StorageBackend
    local_root: Path | None
    local_public_base_url: str | None
    endpoint_url: str | None
    bucket: str
    region: str
    access_key_id: str
    secret_access_key: str
    public_base_url: str | None
    invoice_max_bytes: int


def _parse_backend(raw: str | None) -> StorageBackend:
    value = (raw or "local").strip().lower()
    if value == "s3":
        return "s3"
    return "local"


def _default_local_root() -> Path:
    return Path(os.getenv("ASSET_LOCAL_STORAGE_PATH", "var/asset_uploads")).expanduser().resolve()


@lru_cache(maxsize=1)
def get_storage_settings() -> StorageSettings:
    """Load storage config from environment (used for invoice uploads)."""

    backend = _parse_backend(os.getenv("ASSET_STORAGE_BACKEND"))
    local_root = _default_local_root() if backend == "local" else None
    local_public_raw = os.getenv("ASSET_LOCAL_PUBLIC_BASE_URL")
    local_public_base_url = (
        local_public_raw.strip().rstrip("/") if local_public_raw else None
    )

    bucket = (os.getenv("S3_BUCKET") or "").strip()
    access_key_id = (os.getenv("AWS_ACCESS_KEY_ID") or os.getenv("S3_ACCESS_KEY_ID") or "").strip()
    secret_access_key = (
        os.getenv("AWS_SECRET_ACCESS_KEY") or os.getenv("S3_SECRET_ACCESS_KEY") or ""
    ).strip()
    endpoint_raw = os.getenv("S3_ENDPOINT_URL")
    endpoint_url = endpoint_raw.strip() if endpoint_raw else None
    region = (os.getenv("AWS_REGION") or os.getenv("S3_REGION") or "us-east-1").strip()
    public_raw = os.getenv("S3_PUBLIC_BASE_URL")
    public_base_url = public_raw.strip().rstrip("/") if public_raw else None
    max_mb = int(os.getenv("ASSET_INVOICE_MAX_MB", "10"))
    invoice_max_bytes = max(1, max_mb) * 1024 * 1024

    return StorageSettings(
        backend=backend,
        local_root=local_root,
        local_public_base_url=local_public_base_url,
        endpoint_url=endpoint_url,
        bucket=bucket,
        region=region,
        access_key_id=access_key_id,
        secret_access_key=secret_access_key,
        public_base_url=public_base_url,
        invoice_max_bytes=invoice_max_bytes,
    )


def storage_is_configured(settings: StorageSettings | None = None) -> bool:
    """Return True when invoice uploads can run for the selected backend."""

    cfg = settings or get_storage_settings()
    if cfg.backend == "local":
        return cfg.local_root is not None
    return bool(cfg.bucket and cfg.access_key_id and cfg.secret_access_key)
