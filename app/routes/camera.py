from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates
from app.services.vision_service import gerar_frames_camera

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/monitor")
async def monitor_page(request: Request):
    return templates.TemplateResponse("vision.html", {"request": request})

@router.get("/stream")
async def video_stream():
    """Endpoint que transmite o vídeo processado pela YOLO ao vivo"""
    return StreamingResponse(
        gerar_frames_camera(), 
        media_type="multipart/x-mixed-replace; boundary=frame"
    )