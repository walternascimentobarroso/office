"""Asset invoice storage: local filesystem or S3-compatible."""

from __future__ import annotations

import asyncio
import uuid
from pathlib import Path, PurePosixPath

import boto3
from botocore.client import BaseClient

from app.core.storage_settings import StorageSettings, get_storage_settings, storage_is_configured


def _build_client(settings: StorageSettings) -> BaseClient:
    session = boto3.session.Session(
        aws_access_key_id=settings.access_key_id,
        aws_secret_access_key=settings.secret_access_key,
        region_name=settings.region,
    )
    return session.client(
        "s3",
        endpoint_url=settings.endpoint_url,
    )


def _sanitize_filename(name: str) -> str:
    base = PurePosixPath(name).name
    if not base or base in {".", ".."}:
        return "invoice"
    safe = "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in base)
    return safe[:255] if safe else "invoice"


def _object_key(company_id: uuid.UUID, asset_id: uuid.UUID, filename: str) -> str:
    safe = _sanitize_filename(filename)
    return f"companies/{company_id}/assets/{asset_id}/invoice/{safe}"


def _public_url_s3(settings: StorageSettings, key: str) -> str | None:
    if not settings.public_base_url:
        return None
    return f"{settings.public_base_url}/{key}"


def _ensure_local_root(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)


def _upload_local(
    *,
    root: Path,
    key: str,
    content: bytes,
) -> str | None:
    _ensure_local_root(root)
    dest = root / key
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(content)
    return None


class ObjectStorageService:
    """Upload asset invoices to local disk or S3-compatible storage."""

    def __init__(self, settings: StorageSettings | None = None) -> None:
        self._settings = settings or get_storage_settings()

    def is_ready(self) -> bool:
        return storage_is_configured(self._settings)

    async def upload_asset_invoice(
        self,
        *,
        company_id: uuid.UUID,
        asset_id: uuid.UUID,
        filename: str,
        content: bytes,
        content_type: str | None,
    ) -> tuple[str, str | None]:
        """Upload invoice bytes; return (storage_key, public_url_or_none)."""

        _ = content_type
        if not self.is_ready():
            msg = "Storage is not configured."
            raise RuntimeError(msg)

        key = _object_key(company_id, asset_id, filename)

        if self._settings.backend == "local":
            root = self._settings.local_root
            if root is None:
                msg = "Local storage root is not set."
                raise RuntimeError(msg)

            def _write() -> str | None:
                return _upload_local(root=root, key=key, content=content)

            public: str | None = None
            await asyncio.to_thread(_write)
            if self._settings.local_public_base_url:
                public = f"{self._settings.local_public_base_url}/{key}"
            return key, public

        extra: dict[str, str] = {}
        if content_type:
            extra["ContentType"] = content_type

        def _put() -> None:
            client = _build_client(self._settings)
            client.put_object(
                Bucket=self._settings.bucket,
                Key=key,
                Body=content,
                **extra,
            )

        await asyncio.to_thread(_put)
        return key, _public_url_s3(self._settings, key)

    async def presigned_get_url(self, *, key: str, expires_in: int = 3600) -> str:
        """Return a time-limited URL to download an object (S3 only)."""

        _ = expires_in
        if self._settings.backend == "local":
            msg = "Presigned URLs are only available for S3 backend."
            raise RuntimeError(msg)

        if not self.is_ready():
            msg = "Object storage is not configured (S3_BUCKET and credentials)."
            raise RuntimeError(msg)

        def _url() -> str:
            client = _build_client(self._settings)
            return client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self._settings.bucket, "Key": key},
                ExpiresIn=expires_in,
            )

        return await asyncio.to_thread(_url)
