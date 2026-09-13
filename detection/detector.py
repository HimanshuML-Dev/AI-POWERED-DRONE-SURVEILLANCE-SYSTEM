import cv2
import numpy as np
from models.model_loader import ModelLoader
from detection.classes import COCO_CLASSES, CLASS_COLOR_MAP
from utils.logger import setup_logger

logger = setup_logger("detector")

class ObjectDetector:
    def __init__(self, model_name="yolov8n.pt", conf_thresh=0.45, iou_thresh=0.45, device="cuda"):
        self.conf_thresh = conf_thresh
        self.iou_thresh = iou_thresh
        self.model, self.device = ModelLoader.load_yolo_model(model_name, device)

    def set_thresholds(self, conf_thresh, iou_thresh):
        self.conf_thresh = conf_thresh
        self.iou_thresh = iou_thresh

    def detect_and_track(self, frame, tracker_type="bytetrack.yaml"):
        """Performs detection and persistent tracking using ByteTrack."""
        results = self.model.track(
            source=frame,
            persist=True,
            conf=self.conf_thresh,
            iou=self.iou_thresh,
            tracker=tracker_type,
            device=self.device,
            verbose=False
        )

        detections = []
        if len(results) > 0 and results[0].boxes is not None and len(results[0].boxes) > 0:
            boxes = results[0].boxes
            for box in boxes:
                cls_id = int(box.cls[0].cpu().numpy())
                if cls_id not in COCO_CLASSES:
                    continue

                cls_name = COCO_CLASSES[cls_id]
                conf = float(box.conf[0].cpu().numpy())
                xyxy = box.xyxy[0].cpu().numpy().astype(int)
                
                # Check for track ID assigned by ByteTrack
                track_id = int(box.id[0].cpu().numpy()) if box.id is not None else -1

                detections.append({
                    "track_id": track_id,
                    "class_name": cls_name,
                    "confidence": conf,
                    "bbox": xyxy.tolist(),  # [xmin, ymin, xmax, ymax]
                    "center": [(xyxy[0] + xyxy[2]) // 2, (xyxy[1] + xyxy[3]) // 2]
                })

        return detections