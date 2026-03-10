"""Claude CLI service — calls `claude --print` as async subprocess."""

from __future__ import annotations

import asyncio
import logging

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 120


class ClaudeError(RuntimeError):
    pass


class ClaudeTimeoutError(ClaudeError):
    pass


class ClaudeService:
    """Async wrapper around Claude Code CLI (uses subscription, not API key)."""

    def __init__(
        self,
        *,
        timeout_seconds: int = DEFAULT_TIMEOUT,
        model: str = "sonnet",
    ) -> None:
        self._timeout = timeout_seconds
        self._model = model

    async def chat(self, *, prompt: str) -> str:
        cmd = [
            "claude",
            "--print",
            "--dangerously-skip-permissions",
            "--model", self._model,
            "-p", prompt,
        ]

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(),
                timeout=self._timeout,
            )
        except asyncio.TimeoutError:
            proc.kill()
            raise ClaudeTimeoutError(
                f"Claude CLI timed out after {self._timeout}s"
            )
        except FileNotFoundError:
            raise ClaudeError("Claude CLI not found")

        if proc.returncode != 0:
            err = stderr.decode().strip() if stderr else "unknown error"
            logger.error("Claude CLI failed (rc=%s): %s", proc.returncode, err)
            raise ClaudeError(f"Claude CLI error: {err}")

        result = stdout.decode().strip() if stdout else ""
        if not result:
            raise ClaudeError("Claude CLI returned empty response")

        return result
