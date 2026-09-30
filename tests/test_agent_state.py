import asyncio
from pathlib import Path

import pytest

from orbit.agent import (
    CheckpointStore,
    MemoryStore,
    SubAgentOrchestrator,
)


def test_memory_and_checkpoint_stores_support_resume(tmp_path: Path) -> None:
    memory = MemoryStore(tmp_path / "memory.json")
    memory.remember("session-1", "topic", "local models")
    assert memory.recall("session-1", "topic").value == "local models"

    checkpoints = CheckpointStore(tmp_path / "checkpoints.json")
    checkpoints.save("cp-1", "plan", {"step": 1})
    checkpoints.save("cp-2", "tools", {"step": 2})
    assert checkpoints.rewind("cp-1").state["step"] == 1


@pytest.mark.asyncio
async def test_subagents_run_with_bounded_orchestration() -> None:
    async def discover() -> str:
        await asyncio.sleep(0)
        return "sources"

    async def verify() -> str:
        await asyncio.sleep(0)
        return "verified"

    results = await SubAgentOrchestrator(max_concurrency=1).run(
        {"discover": discover, "verify": verify}
    )

    assert [(result.name, result.output) for result in results] == [
        ("discover", "sources"),
        ("verify", "verified"),
    ]