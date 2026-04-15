import cv2
from pathlib import Path
import torch
import ultralytics.nn.tasks as ultratasks
from ultralytics import YOLO
import numpy as np


def _patch_ultralytics_torch_safe_load():
    from ultralytics.nn.tasks import temporary_modules, check_suffix, check_requirements
    from ultralytics.utils.downloads import attempt_download_asset

    def torch_safe_load(weight):
        check_suffix(file=weight, suffix='.pt')
        file = attempt_download_asset(weight)
        try:
            with temporary_modules(
                {
                    'ultralytics.yolo.utils': 'ultralytics.utils',
                    'ultralytics.yolo.v8': 'ultralytics.models.yolo',
                    'ultralytics.yolo.data': 'ultralytics.data',
                }
            ):
                torch.serialization.add_safe_globals(
                    [
                        ultratasks.DetectionModel,
                        torch.nn.modules.container.Sequential,
                        torch.nn.modules.module.Module,
                        torch.nn.parameter.Parameter,
                    ]
                )
                return torch.load(file, map_location='cpu', weights_only=False), file
        except ModuleNotFoundError as e:
            if e.name == 'models':
                raise e
            check_requirements(e.name)
            torch.serialization.add_safe_globals(
                [
                    ultratasks.DetectionModel,
                    torch.nn.modules.container.Sequential,
                    torch.nn.modules.module.Module,
                    torch.nn.parameter.Parameter,
                ]
            )
            return torch.load(file, map_location='cpu', weights_only=False), file

    ultratasks.torch_safe_load = torch_safe_load


_patch_ultralytics_torch_safe_load()
model_path = Path(__file__).resolve().parent.parent / 'models' / 'modelv0.5.pt'
model = YOLO(str(model_path))

def gerar_frames_camera():
    """Captura a câmera, processa com YOLO e converte para streaming Web"""
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        raise RuntimeError("Erro: Não foi possível acessar a câmera.")

    class_names = model.names

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Inferência YOLOv8
            results = model(frame, conf=0.5)

            # Processa e desenha
            for r in results:
                boxes = r.boxes.xyxy.cpu().numpy()
                confidences = r.boxes.conf.cpu().numpy()
                class_ids = r.boxes.cls.cpu().numpy()

                for box, conf, class_id in zip(boxes, confidences, class_ids):
                    x1, y1, x2, y2 = map(int, box)
                    label = f"{class_names[int(class_id)]}: {conf:.2f}"

                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Transforma a imagem processada em um formato JPEG que a Web entende
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()

            # "Yield" envia o frame imediatamente sem fechar a conexão
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    finally:
        cap.release()