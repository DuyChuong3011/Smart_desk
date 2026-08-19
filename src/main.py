import cv2
import yaml
import logging
import os
import sys

# Add the project root to sys.path so we can import src modules if run from other dirs
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.camera import CameraManager
from src.detector import ObjectDetector
from src.roi import ROIManager
from src.state_manager import StateManager
from src.event_manager import EventManager
from src.mqtt_client import SmartDeskMQTTClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_config():
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'config.yaml')
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def draw_hud(frame, inventory, roi_manager):
    # Draw ROI
    cv2.rectangle(frame, (roi_manager.x1, roi_manager.y1), (roi_manager.x2, roi_manager.y2), (0, 255, 0), 2)
    cv2.putText(frame, "Desk ROI", (roi_manager.x1, roi_manager.y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    # Draw Inventory
    y_offset = 30
    cv2.putText(frame, "Smart Desk Inventory", (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    y_offset += 30
    
    for obj, status in inventory.items():
        color = (0, 255, 0)
        text = f"{obj.capitalize()}: PRESENT"
        cv2.putText(frame, text, (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        y_offset += 25

def main():
    config = load_config()
    
    camera = CameraManager(config)
    detector = ObjectDetector(config)
    roi_manager = ROIManager(config)
    state_manager = StateManager(config)
    
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
    event_manager = EventManager(config, log_dir)
    
    mqtt_client = SmartDeskMQTTClient(config)
    mqtt_client.connect()
    
    if not camera.open():
        return
    
    try:
        frame_count = 0
        desk_objects = []
        skip_frames = config['detection'].get('skip_frames', 1)
        
        while True:
            ret, frame = camera.read_frame()
            if not ret:
                logging.error("Failed to read frame")
                break
                
            frame_count += 1
            
            # Chỉ chạy nhận diện AI sau mỗi X frames để giảm tải CPU
            if frame_count % skip_frames == 0:
                # 1. Detect objects (with tracking)
                all_detections = detector.detect(frame)
                
                # 2. Filter by ROI
                desk_objects = roi_manager.filter_detections(all_detections)
                
                # 3. Update State
                state_changes = state_manager.update_state(desk_objects)
                
                # 4. Process Events and Save Snapshots
                if state_changes:
                    # Save the raw frame without HUD as snapshot
                    event_manager.process_events(state_changes, frame.copy())
                    for change in state_changes:
                        mqtt_client.publish_event(change['event'], change['object'])
                
            # Visualization (Vẫn vẽ liên tục mỗi frame dựa trên kết quả cũ)
            inventory = state_manager.get_inventory()
            
            # Draw bounding boxes for detected objects in ROI
            for obj in desk_objects:
                x1, y1, x2, y2 = obj['bbox']
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                # Show class and track_id
                label = f"{obj['class']}_{obj['track_id']} {obj['confidence']:.2f}"
                cv2.putText(frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                
            draw_hud(frame, inventory, roi_manager)
            
            cv2.imshow("Smart Desk (Tracking & Snapshot)", frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except KeyboardInterrupt:
        logging.info("Stopping Smart Desk...")
    finally:
        mqtt_client.disconnect()
        camera.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
