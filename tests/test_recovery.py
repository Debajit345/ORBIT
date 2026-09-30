from pathlib import Path

import pytest

from orbit.observability import JsonEventLogger
from orbit.storage import BackupManager, BackupScheduler
from orbit.updater import UpdateArtifact, UpdateManager


def test_backup_restore_and_structured_events(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "state.json").write_text('{"ready": true}', encoding="utf-8")
    archive = tmp_path / "backup.zip"
    restored = tmp_path / "restored"

    BackupManager().create(source, archive)
    BackupManager().restore(archive, restored)
    JsonEventLogger(tmp_path / "events.jsonl").emit(
        "backup.created",
        archive=str(archive),
    )

    assert (restored / "state.json").read_text(encoding="utf-8") == '{"ready": true}'
    assert "backup.created" in (tmp_path / "events.jsonl").read_text(encoding="utf-8")


def test_restore_rejects_zip_path_traversal(tmp_path: Path) -> None:
    archive = tmp_path / "unsafe.zip"
    import zipfile

    with zipfile.ZipFile(archive, "w") as handle:
        handle.writestr("../escape.txt", "unsafe")

    with pytest.raises(ValueError, match="unsafe path"):
        BackupManager().restore(archive, tmp_path / "restored")


def test_backup_scheduler_and_checksum_verified_updates(tmp_path: Path) -> None:
    from datetime import timedelta
    import hashlib

    source = tmp_path / "source"
    source.mkdir()
    (source / "state").write_text("state", encoding="utf-8")
    scheduler = BackupScheduler(BackupManager(), timedelta(hours=1))
    assert scheduler.due()
    scheduler.run(source, tmp_path / "scheduled.zip")
    assert not scheduler.due()

    artifact = tmp_path / "orbit.msi"
    artifact.write_bytes(b"installer")
    checksum = hashlib.sha256(artifact.read_bytes()).hexdigest()
    staged = UpdateManager().stage(
        UpdateArtifact(artifact, checksum, "0.2.0"),
        tmp_path / "updates",
    )
    assert staged.read_bytes() == b"installer"