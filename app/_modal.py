import json
from typing import Dict

from fastapi import FastAPI
from modal import App, Image, Secret, asgi_app

from app.settings import settings

name = "modal-comfyui-example"
app = App(name=name)

_app_env_dict: Dict[str, str | None] = {
    f"APP_{str(k)}": str(v) for k, v in json.loads(settings.model_dump_json()).items()
}
app_env = Secret.from_dict(_app_env_dict)

app_image = (
    Image.debian_slim()
    .apt_install("git")  # install git to clone ComfyUI
    .pip_install(["uv", "comfy-cli>=1.2.7"])
    .run_commands("comfy --skip-prompt install --nvidia")
    .run_commands(
        [
            "comfy --skip-prompt model download --url https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp8_e4m3fn.safetensors --relative-path models/clip",
            "comfy --skip-prompt model download --url https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/clip_l.safetensors --relative-path models/clip",
            "comfy --skip-prompt model download --url https://huggingface.co/black-forest-labs/FLUX.1-schnell/resolve/main/ae.safetensors --relative-path models/vae",
            "comfy --skip-prompt model download --url https://huggingface.co/black-forest-labs/FLUX.1-schnell/resolve/main/flux1-schnell.safetensors --relative-path models/unet",
        ]
    )
    .run_commands(  # download a custom node
        "comfy node install image-resize-comfyui"
    )
    .copy_local_file(
        "static/comfyui/workflow_api.json", "/root/comfy/ComfyUI/workflow_api.json"
    )
    .workdir("/work")
    .copy_local_file("pyproject.toml", "/work/pyproject.toml")
    .copy_local_file("uv.lock", "/work/uv.lock")
    .env({"UV_PROJECT_ENVIRONMENT": "/usr/local"})
    .run_commands(
        [
            "uv sync --frozen --compile-bytecode",
            "uv build",
        ]
    )
)


@app.function(
    allow_concurrent_inputs=10,
    concurrency_limit=1,
    container_idle_timeout=30,
    cpu=2.0,
    gpu="A10G",
    image=app_image,
    memory=4096,
    secrets=[app_env],
    timeout=1800,
)
@asgi_app(label=name)
def _app() -> FastAPI:
    from app.main import app

    return app
