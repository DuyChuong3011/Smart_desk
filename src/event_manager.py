import logging
from src.storage import EventDatabase
import os
import cv2
from datetime import datetime

class EventManager:
    def __init__(self, config, log_dir="logs"):
        self.log_dir = log_dir
        self.snapshot_dir = config['outputs'].get('snapshot_dir', 'outputs/snapshots')
        
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        if not os.path.exists(self.snapshot_dir):
            os.makedirs(self.snapshot_dir)
            
        self.db = EventDatabase(os.path.join(self.log_dir, "smart_desk.db"))

    def process_events(self, state_changes, frame):
        for change in state_changes:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            filename_ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            obj = change['object']
            event = change['event']
            
            logging.info(f"EVENT: {event} | OBJECT: {obj}")
            
            # Save snapshot
            snapshot_filename = f"{filename_ts}_{obj}_{event}.jpg"
            snapshot_path = os.path.join(self.snapshot_dir, snapshot_filename)
            
            if frame is not None:
                # Save the raw frame image
                cv2.imwrite(snapshot_path, frame)
            
            # Insert into database
            self.db.insert_event(timestamp, obj, event, snapshot_filename)
