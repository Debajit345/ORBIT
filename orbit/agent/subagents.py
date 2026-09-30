"""Bounded sub-agent orchestration."""

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class SubAgentResult:
    """Result from one named sub-agent."""

    name: str
    output: str


class SubAgentOrchestrator:
    """Run independent sub-agents concurrently with a bounded limit."""

    def __init__(self, max_concurrency: int = 3) -> None:
        self.max_concurrency = max(1, max_concurrency)

    async def run(
        self,
        tasks: dict[str, Callable[[], Awaitable[str]]],
    ) -> list[SubAgentResult]:
        semaphore = asyncio.Semaphore(self.max_concurrency)

        async def execute(name: str, task: Callable[[], Awaitable[str]]) -> SubAgentResult:
            async with semaphore:
                return SubAgentResult(name, await task())

        results = await asyncio.gather(
            *(execute(name, task) for name, task in tasks.items())
        )
        return list(results)