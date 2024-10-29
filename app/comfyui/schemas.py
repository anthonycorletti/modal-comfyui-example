import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict

from pydantic import BaseModel


@dataclass
class ComfyuiWorkflow:
    content: Dict
    path: str

    @staticmethod
    def from_json_file(path: str) -> "ComfyuiWorkflow":
        return ComfyuiWorkflow(path=path, content=json.loads(Path(path).read_text()))

    def set_prompt(self, prompt: str) -> None:
        self.content["6"]["inputs"]["text"] = prompt

    def set_client_id(self, client_id: str) -> None:
        self.content["9"]["inputs"]["filename_prefix"] = client_id


class ComfyuiInferRequest(BaseModel):
    prompt: str
