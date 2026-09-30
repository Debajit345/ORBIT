"""Path-safe local backup and restore support."""

from pathlib import Path
from datetime import datetime, timedelta, timezone
import zipfile


class BackupManager:
    """Create and restore ZIP backups for local ORBIT data."""

    def create(self, source: Path, destination: Path) -> Path:
        """Create a compressed backup of a file or directory."""

        source = source.resolve()
        destination = destination.resolve()
        destination.parent.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(
            destination,
            "w",
            compression=zipfile.ZIP_DEFLATED,
        ) as archive:
            if source.is_file():
                archive.write(source, source.name)
            else:
                for path in source.rglob("*"):
                    if path.is_file():
                        archive.write(path, path.relative_to(source))

        return destination

    def restore(self, archive_path: Path, destination: Path) -> None:
        """Restore a backup while rejecting path traversal entries."""

        destination = destination.resolve()
        destination.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(archive_path) as archive:
            for member in archive.infolist():
                target = (destination / member.filename).resolve()
                if destination not in target.parents and target != destination:
                    raise ValueError("Backup contains an unsafe path")

            archive.extractall(destination)


class BackupScheduler:
    """Calculate and execute periodic backups for a local data root."""

    def __init__(self, manager: BackupManager, interval: timedelta) -> None:
        if interval <= timedelta(0):
            raise ValueError("Backup interval must be positive")
        self.manager = manager
        self.interval = interval
        self.last_backup_at: datetime | None = None

    def due(self, now: datetime | None = None) -> bool:
        """Return whether a backup should run now."""

        current = now or datetime.now(timezone.utc)
        return self.last_backup_at is None or current >= self.last_backup_at + self.interval

    def run(
        self,
        source: Path,
        destination: Path,
        *,
        now: datetime | None = None,
    ) -> Path:
        """Create a backup and update the schedule marker."""

        backup = self.manager.create(source, destination)
        self.last_backup_at = now or datetime.now(timezone.utc)
        return backup