from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.services.vision_service import gerar_frames_camera

router = APIRouter()

@router.get("/stream")
async def video_stream():
    """Endpoint que transmite o vídeo processado pela YOLO ao vivo"""
    return StreamingResponse(
        gerar_frames_camera(), 
        media_type="multipart/x-mixed-replace; boundary=frame"
    )