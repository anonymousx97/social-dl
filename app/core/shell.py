import asyncio
import os


async def take_ss(video: str, path: str):
    thumb = f"{path}/i.png"
    await run_shell_cmd(
        f'''ffmpeg -hide_banner -loglevel error -ss 0.1 -i "{video}" -vframes 1 "{thumb}"'''
    )
    if os.path.isfile(thumb):
        return thumb


async def check_audio(file):
    result = await run_shell_cmd(
        f"ffprobe -v error -show_entries format=nb_streams -of default=noprint_wrappers=1:nokey=1 {file}"
    )
    return int(result or 0) - 1


async def run_shell_cmd(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT
    )
    stdout, _ = await proc.communicate()
    return stdout.decode("utf-8")


class AsyncShell:
    full_std = ""
    is_not_completed = True

    def __init__(self, process):
        self.process = process

    async def get_output(self):
        while True:
            # Check output and stop loop if it's emtpy
            line = (await self.process.stdout.readline()).decode("utf-8")
            if not line:
                break
            self.full_std += line
        # Let the Subprocess complete and let it shut down
        await self.process.wait()
        self.is_not_completed = False

    @classmethod
    async def run_cmd(cls, cmd):
        # Create Subprocess and initialise self using cls
        sub_process = cls(
            process=await asyncio.create_subprocess_shell(
                cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT
            )
        )
        # Start Checking output but don't block code by awaiting it.
        asyncio.create_task(sub_process.get_output())
        # Sleep for a short time to let previous task start
        await asyncio.sleep(0.5)
        # Return Self object
        return sub_process
