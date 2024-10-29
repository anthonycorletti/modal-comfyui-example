import json
import subprocess
from pathlib import Path
from tempfile import NamedTemporaryFile

import structlog

from app.comfyui.schemas import ComfyuiWorkflow
from app.settings import settings

log = structlog.get_logger()


class ComfyuiService:
    async def infer(self, workflow: ComfyuiWorkflow) -> bytes | None:
        with NamedTemporaryFile(mode="w+", suffix=".json") as tfile:
            content = json.dumps(workflow.content)
            tfile.write(content)
            # assert that the content is written to the file
            tfile.seek(0)
            written_content = tfile.read()
            assert content == written_content
            cmd = f"comfy run --workflow {tfile.name} --wait --timeout 1200"
            out = subprocess.run(
                cmd, shell=True, check=False, capture_output=True, text=True
            )
            if out.returncode != 0:
                log.error("-------------------------------------------------")
                log.error("ComfyUI workflow failed", returncode=out.returncode)
                log.error("stdout", content=out.stdout)
                log.error("stderr", content=out.stderr)
                log.error("-------------------------------------------------")
                return None

            file_prefix = [
                node.get("inputs")
                for node in workflow.content.values()
                if node.get("class_type") == "SaveImage"
            ][0]["filename_prefix"]
            log.debug("file_prefix", file_prefix=file_prefix)
            # returns the image as bytes
            for path in Path(settings.COMFYUI_OUTPUT_DIR).iterdir():
                log.debug("Checking file", path=path)
                if path.name.startswith(file_prefix):
                    log.debug("Found image!", path=path)
                    return path.read_bytes()

        return None
