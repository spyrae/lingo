from __future__ import annotations

import asyncio
import os
import subprocess
import contextlib
from dataclasses import dataclass


class CodexNotInstalledError(RuntimeError):
    pass


class CodexTimeoutError(RuntimeError):
    pass


@dataclass(frozen=True)
class CodexChatRequest:
    prompt: str
    timeout_seconds: int


class CodexService:
    """
    Thin wrapper around Codex CLI.

    NOTE: Codex CLI flags can vary by installation; we keep invocation conservative:
    - feed full prompt via stdin
    - rely on environment (OPENAI_API_KEY) being present
    """

    def __init__(self, *, command: str = "codex", timeout_seconds: int = 60) -> None:
        self._command = command
        self._timeout_seconds = timeout_seconds

    async def chat(self, *, prompt: str) -> str:
        req = CodexChatRequest(prompt=prompt, timeout_seconds=self._timeout_seconds)
        return await self._run(req)

    async def _run(self, req: CodexChatRequest) -> str:
        env = os.environ.copy()
        if not env.get("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY is not set (required for Codex CLI)")

        try:
            proc = await asyncio.create_subprocess_exec(
                self._command,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
            )
        except FileNotFoundError as e:
            raise CodexNotInstalledError(
                f"Codex CLI not found: '{self._command}'. Install Codex CLI or set CODEX_COMMAND."
            ) from e

        try:
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(input=req.prompt.encode("utf-8")),
                timeout=req.timeout_seconds,
            )
        except asyncio.TimeoutError as e:
            with contextlib.suppress(Exception):
                proc.kill()
            raise CodexTimeoutError("Codex CLI timed out") from e

        if proc.returncode != 0:
            err = (stderr or b"").decode("utf-8", errors="replace").strip()
            raise subprocess.CalledProcessError(proc.returncode or 1, self._command, err)

        out = (stdout or b"").decode("utf-8", errors="replace").strip()
        return out

