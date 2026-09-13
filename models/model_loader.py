import torch
from ultralytics import YOLO
from utils.logger import setup_logger

logger = setup_logger("model_loader")

class ModelLoader:
    @staticmethod
    def load_yolo_model(model_name="yolov8n.pt", device_pref="cuda"):
        if device_pref == "cuda" and torch.cuda.is_available():
            device = "cuda"
            device_name = torch.cuda.get_device_name(0)
            logger.info(f"Using NVIDIA GPU Acceleration: {device_name}")
        else:
            device = "cpu"
            logger.info("CUDA unavailable or CPU selected. Falling back to CPU inference.")

        try:
            model = YOLO(model_name)
            model.to(device)
            logger.info(f"YOLO Model '{model_name}' loaded successfully on {device.upper()}.")
            return model, device
        except Exception as e:
            logger.error(f"Failed to load YOLO model: {e}")
            raise RuntimeError(f"Could not initialize object detector: {e}")