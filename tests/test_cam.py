from ultralytics import YOLO
import cv2
import os
import sys
import threading
import time
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

RTSP_URL = os.getenv("RTSP_URL")

# Modelo treinado especificamente para Garrafas de Água
MODEL_PATH = r'models/modelv0.5pt'

# Configurações de exibição
WINDOW_NAME = "Monitoramento de Estoque - YOLOv8"
CONFIDENCE_THRESHOLD = 0.50
TARGET_CLASSES = []

# Classe para ler o RTSP em segundo plano (evita delay/lag)
class VideoCaptureThreading:
    def __init__(self, src):
        os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"
        self.cap = cv2.VideoCapture(src, cv2.CAP_FFMPEG)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.ret, self.frame = self.cap.read()
        self.stopped = False
        self.lock = threading.Lock()
        
        # Inicia a thread que vai ler os frames sem parar
        self.thread = threading.Thread(target=self.update, args=(), daemon=True)
        self.thread.start()

    def update(self):
        # Loop infinito para sempre pegar o frame mais recente e descartar os velhos
        while not self.stopped:
            if not self.cap.isOpened():
                self.stopped = True
                break
            
            # Lê o próximo frame o mais rápido possível
            ret, frame = self.cap.read()
            with self.lock:
                self.ret = ret
                self.frame = frame

    def read(self):
        with self.lock:
            return self.ret, self.frame.copy() if self.ret else None

    def stop(self):
        self.stopped = True
        self.thread.join()
        self.cap.release()

def main():
    print("--- INICIANDO SISTEMA DE MONITORAMENTO DE ESTOQUE ---")
    
    # 1. Carregar o modelo YOLO
    print(f"Carregando modelo {MODEL_PATH}...")
    try:
        model = YOLO(MODEL_PATH)
        print("Modelo carregado com sucesso!")
    except Exception as e:
        print(f"Erro ao carregar modelo: {e}")
        sys.exit(1)

    # 2. Configurar conexão com a câmera usando Thread
    print(f"Conectando à câmera: {RTSP_URL}")
    cap = VideoCaptureThreading(RTSP_URL)

    time.sleep(1) # Aguarda 1 seg para garantir que o stream começou

    if not cap.ret:
        print("Erro: Não foi possível abrir o stream da câmera.")
        cap.stop()
        sys.exit(1)

    # 3. Configurar janela
    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW_NAME, 1024, 768)

    print("Iniciando loop de detecção. Pressione 'q' para sair.")
    
    frame_count = 0
    last_results = None

    try:
        while True:
            # Pega o frame MAIS RECENTE da thread
            ret, frame = cap.read()
            if not ret or frame is None:
                # Se não houver frame novo, tenta de novo
                continue

            frame_count += 1
            
            # Reduzir resolução para inferência (opcional, mas ajuda)
            # frame_resized = cv2.resize(frame, (640, 480)) 

            # 4. Realizar a detecção (Inference)
            # stream=True é mais eficiente para vídeos longos
            results = model(frame, conf=CONFIDENCE_THRESHOLD, verbose=False)
            last_results = results[0]

            # 5. Processar resultados
            result = results[0]
            
            # Contagem de objetos detectados no frame atual
            detections_count = {}
            
            for box in result.boxes:
                cls_id = int(box.cls[0])
                class_name = model.names[cls_id]
                
                # Filtrar se necessário
                if TARGET_CLASSES and cls_id not in TARGET_CLASSES:
                    continue
                    
                detections_count[class_name] = detections_count.get(class_name, 0) + 1

            # 6. Desenhar resultados no frame
            # plot() retorna o frame com as caixas desenhadas
            annotated_frame = result.plot()

            # 7. Adicionar painel de contagem na tela
            y_offset = 30
            cv2.putText(annotated_frame, "CONTAGEM ATUAL:", (10, y_offset), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            for cls_name, count in detections_count.items():
                y_offset += 30
                text = f"{cls_name.upper()}: {count}"
                cv2.putText(annotated_frame, text, (10, y_offset), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

            # 8. Exibir
            # Vamos redimensionar a imagem final para caber melhor na tela e tirar o aspecto de "zoom"
            display_frame = cv2.resize(annotated_frame, (1024, 768)) # Mantendo uma resolução boa
            cv2.imshow(WINDOW_NAME, display_frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("\nInterrompido pelo usuário.")
    finally:
        if hasattr(cap, 'stop'):
            cap.stop()
        else:
            cap.release()
        cv2.destroyAllWindows()
        print("Sistema encerrado.")

if __name__ == "__main__":
    main()