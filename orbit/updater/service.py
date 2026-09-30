"""Checksum-verified local update staging."""

from dataclasses import dataclass
import hashlib
from pathlib import Path
import shutil
import tempfile


@dataclass(frozen=True)
class UpdateArtifact:
    """A downloaded update artifact and its expected SHA-256 checksum."""

    path: Path
    sha256: str
    version: str


class UpdateManager:
    """Verify and stage updates without replacing a live installation."""

    def verify(self, artifact: UpdateArtifact) -> None:
        """Verify an artifact checksum before it can be staged."""

        digest = hashlib.sha256(artifact.path.read_bytes()).hexdigest()
        if digest.lower() != artifact.sha256.lower():
            raise ValueError("Update checksum mismatch")

    def stage(self, artifact: UpdateArtifact, destination: Path) -> Path:
        """Verify and copy an artifact into an isolated staging directory."""

        self.verify(artifact)
        staging = destination / artifact.version
        staging.mkdir(parents=True, exist_ok=True)
        target = staging / artifact.path.name
        shutil.copy2(artifact.path, target)
        return target