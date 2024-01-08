import asyncio
import os
from typing import AsyncIterable


async def run_shell_cmd(cmd: str) -> str:
    proc: asyncio.create_subprocess_shell = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT
    )
    stdout, _ = await proc.communicate()
    return stdout.decode("utf-8")


async def take_ss(video: str, path: str) -> None | str:
    thumb = f"{path}/i.png"
    await run_shell_cmd(
        f'''ffmpeg -hide_banner -loglevel error -ss 0.1 -i "{video}" -vframes 1 "{thumb}"'''
    )
    if os.path.isfile(thumb):
        return thumb


async def check_audio(file) -> int:
    result = await run_shell_cmd(
        f"ffprobe -v error -show_entries format=nb_streams -of default=noprint_wrappers=1:nokey=1 {file}"
    )
    return int(result or 0) - 1


async def get_duration(file) -> int:
    duration = await run_shell_cmd(
        f"""ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {file}"""
    )
    return round(float(duration.strip() or 0))


class AsyncShell:
    def __init__(self, process: asyncio.create_subprocess_shell):
        self.process: asyncio.create_subprocess_shell = process
        self.full_std: str = ""
        self.is_done: bool = False
        self._task: asyncio.Task | None = None

    async def read_output(self) -> None:
        while True:
            line: str = (await self.process.stdout.readline()).decode("utf-8")
            if not line:
                break
            self.full_std += line
        self.is_done = True
        await self.process.wait()

    async def get_output(self) -> AsyncIterable:
        while not self.is_done:
            yield self.full_std

    def cancel(self) -> None:
        if not self.is_done:
            self.process.kill()
            self._task.cancel()

    @classmethod
    async def run_cmd(cls, cmd: str, name: str = "AsyncShell") -> "AsyncShell":
        sub_process: AsyncShell = cls(
            process=await asyncio.create_subprocess_shell(
                cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT
            )
        )
        sub_process._task = asyncio.create_task(sub_process.read_output(), name=name)
        await asyncio.sleep(0.5)
        return sub_process
