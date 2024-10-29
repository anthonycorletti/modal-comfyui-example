from uuid import uuid4

import structlog
from fastapi import APIRouter, Depends, Response

from app.comfyui.schemas import ComfyuiInferRequest, ComfyuiWorkflow
from app.comfyui.service import ComfyuiService
from app.settings import settings

router = APIRouter(tags=["comfyui"])
log = structlog.get_logger()


class Routes:
    infer = "/infer"


@router.post(Routes.infer, response_class=Response)
async def infer(
    req: ComfyuiInferRequest, cui_svc: ComfyuiService = Depends(ComfyuiService)
) -> Response:
    log.info("infer request", prompt=req.prompt)
    wf = ComfyuiWorkflow.from_json_file(settings.COMFYUI_WORKFLOW_PATH)
    wf.set_prompt(req.prompt)
    wf.set_client_id(uuid4().hex)
    log.info("workflow", wf=wf.content)
    log.info("running comfy ui workflow...")
    image_bytes = await cui_svc.infer(wf)
    log.info("inference complete")
    return Response(image_bytes, media_type="image/jpeg")
