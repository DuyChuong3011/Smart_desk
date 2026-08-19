import math

class StateManager:
    def __init__(self, config):
        self.max_missed_frames = config['tracking']['max_missed_frames']
        self.move_distance_threshold = config['tracking'].get('move_distance_threshold', 50)
        
        # State schema:
        # {
        #   "mouse_1": {"status": "PRESENT", "missed_frames": 0, "center": (x,y), "class": "mouse"},
        #   ...
        # }
        self.inventory = {}

    def update_state(self, current_detections):
        state_changes = []
        
        # Map current detections by a unique key (class + track_id)
        current_objects = {}
        for d in current_detections:
            if d['track_id'] == -1: continue # Ignore objects without tracking ID
            obj_key = f"{d['class']}_{d['track_id']}"
            current_objects[obj_key] = d

        # Update existing objects and find removals/movements
        for obj_key, state_data in list(self.inventory.items()):
            if obj_key in current_objects:
                detection = current_objects[obj_key]
                state_data['missed_frames'] = 0
                
                # Check for movement
                old_center = state_data['center']
                new_center = detection['center']
                dist = math.hypot(new_center[0] - old_center[0], new_center[1] - old_center[1])
                
                if dist > self.move_distance_threshold:
                    state_changes.append({"object": obj_key, "event": "MOVED", "detection": detection})
                    
                state_data['center'] = new_center
            else:
                # Object is NOT present in current frame
                state_data['missed_frames'] += 1
                
                if state_data['missed_frames'] >= self.max_missed_frames:
                    state_changes.append({"object": obj_key, "event": "REMOVED", "detection": None})
                    # Remove from inventory completely
                    del self.inventory[obj_key]

        # Find new objects
        for obj_key, detection in current_objects.items():
            if obj_key not in self.inventory:
                self.inventory[obj_key] = {
                    "status": "PRESENT", 
                    "missed_frames": 0, 
                    "center": detection['center'],
                    "class": detection['class']
                }
                state_changes.append({"object": obj_key, "event": "APPEARED", "detection": detection})

        return state_changes

    def get_inventory(self):
        # We only keep PRESENT objects in inventory now
        return {k: v['status'] for k, v in self.inventory.items()}
