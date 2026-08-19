from ultralytics import YOLO
import logging

class ObjectDetector:
    def __init__(self, config):
        self.config = config['detection']
        logging.info(f"Loading YOLO model: {self.config['model_path']}")
        self.model = YOLO(self.config['model_path'])
        self.target_classes = self.config['target_classes']
        self.confidence_threshold = self.config['confidence']
        self.imgsz = self.config.get('imgsz', 640)
        # Map class names to IDs to filter YOLO output easily
        self.class_names = self.model.names
        self.target_class_ids = [k for k, v in self.class_names.items() if v in self.target_classes]

    def detect(self, frame):
        # Use track() instead of call() to assign persistent IDs
        results = self.model.track(frame, persist=True, verbose=False, imgsz=self.imgsz)[0]
        detections = []
        
        for box in results.boxes:
            cls_id = int(box.cls[0].item())
            conf = box.conf[0].item()
            # ByteTrack/DeepSORT assigns IDs
            track_id = int(box.id[0].item()) if box.id is not None else -1
            
            if cls_id in self.target_class_ids and conf >= self.confidence_threshold:
                class_name = self.class_names[cls_id]
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                
                detections.append({
                    "track_id": track_id,
                    "class": class_name,
                    "confidence": conf,
                    "bbox": (int(x1), int(y1), int(x2), int(y2)),
                    "center": (int((x1 + x2) / 2), int((y1 + y2) / 2))
                })
        return detections
